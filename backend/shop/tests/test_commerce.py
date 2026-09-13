from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from threading import Barrier
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction, close_old_connections, connection, connections
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from shop import models as m
from shop import services as s

pytestmark = pytest.mark.django_db


def test_database_rejects_overreserved(stock):
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Inventory.objects.filter(pk=stock.pk).update(reserved=6)


def test_unique_size_sku(stock):
    with pytest.raises(IntegrityError), transaction.atomic():
        m.VariantSize.objects.create(
            variant=stock.variant_size.variant, size=stock.variant_size.size, sku="OTHER"
        )


def test_one_default_variant(stock):
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Variant.objects.create(
            product=stock.variant_size.variant.product,
            sku="SECOND",
            color_name="White",
            color_family="white",
            is_default=True,
        )


def test_cart_reprices_database_value(bag, stock):
    assert s.price_cart(bag)["subtotal"] == "10000.00"
    variant = stock.variant_size.variant
    variant.price = Decimal("12345.67")
    variant.save()
    assert s.price_cart(bag)["subtotal"] == "12345.67"


def test_unpublished_size_cannot_checkout(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    product = stock.variant_size.variant.product
    product.status = "draft"
    product.save()
    with pytest.raises(ValidationError):
        s.create_checkout(bag, checkout_data, "draft")
    assert not m.Order.objects.exists()


def test_checkout_reserves_then_verified_event_consumes(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "reserve")
    stock.refresh_from_db()
    assert (stock.on_hand, stock.reserved) == (5, 1)
    assert order.status == "payment_pending"
    s.confirm_payment(order.reference, "evt1", "test", order.total, "KES")
    stock.refresh_from_db()
    assert (stock.on_hand, stock.reserved) == (4, 0)
    order.refresh_from_db()
    assert order.status == "paid"


def test_checkout_idempotency_and_changed_body(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    first = s.create_checkout(bag, checkout_data, "same")
    assert s.create_checkout(bag, checkout_data, "same").pk == first.pk
    with pytest.raises(ValidationError):
        s.create_checkout(bag, {**checkout_data, "phone": "+254711111111"}, "same")
    assert m.Reservation.objects.count() == 1


def test_second_pending_attempt_rejected(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    s.create_checkout(bag, checkout_data, "first")
    with pytest.raises(ValidationError):
        s.create_checkout(bag, checkout_data, "second")


@pytest.mark.parametrize(
    "amount,currency,provider",
    [("0.01", "KES", "test"), ("10350.00", "USD", "test"), ("10350.00", "KES", "stripe")],
)
def test_invalid_payment_never_fulfills(
    bag, stock, checkout_data, settings, amount, currency, provider
):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "invalid")
    with pytest.raises(ValidationError):
        s.confirm_payment(order.reference, "evil", provider, amount, currency)
    stock.refresh_from_db()
    assert stock.on_hand == 5
    order.refresh_from_db()
    assert order.status == "payment_pending"


def test_payment_replay_exactly_once(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "replay")
    for event_id in ["evt", "evt", "evt-second"]:
        s.confirm_payment(order.reference, event_id, "test", order.total, "KES")
    stock.refresh_from_db()
    assert stock.on_hand == 4
    assert m.PaymentEvent.objects.count() == 1


def test_expiry_releases_stock_and_promotion(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    m.Promotion.objects.create(code="TEN", name="Ten", kind="percent", value=10)
    bag.promo_code = "TEN"
    bag.save()
    order = s.create_checkout(bag, checkout_data, "expiry")
    m.Order.objects.filter(pk=order.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
    assert s.expire_order(order.pk)
    assert not s.expire_order(order.pk)
    stock.refresh_from_db()
    assert stock.reserved == 0
    assert m.Promotion.objects.get(code="TEN").uses == 0
    with pytest.raises(ValidationError):
        s.confirm_payment(order.reference, "late", "test", order.total, "KES")


def test_promotion_limits_and_exact_decimals(bag, stock):
    m.Promotion.objects.create(
        code="TEN", name="Ten percent", kind="percent", value="10.00", minimum=5000
    )
    bag.promo_code = "TEN"
    bag.save()
    assert s.price_cart(bag)["discount"] == "1000.00"
    m.Promotion.objects.filter(code="TEN").update(uses=1000)
    assert s.price_cart(bag)["discount"] == "0.00"
    with pytest.raises(ValidationError):
        s.price_cart(bag, strict=True)


def test_promotion_scope_excludes_unmatched_brand(bag):
    other = m.Brand.objects.create(name="Other", slug="other")
    promo = m.Promotion.objects.create(code="OTHER", name="Other", kind="fixed", value=90000)
    promo.brands.add(other)
    bag.promo_code = "OTHER"
    bag.save()
    assert s.price_cart(bag)["discount"] == "0.00"


def test_discount_never_makes_total_negative(bag):
    m.Promotion.objects.create(code="HUGE", name="Huge", kind="fixed", value=90000)
    bag.promo_code = "HUGE"
    bag.save()
    assert Decimal(s.price_cart(bag)["total"]) >= 0


def test_order_snapshots_survive_catalog_change(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "snapshot")
    p = stock.variant_size.variant.product
    p.name = "Changed"
    p.base_price = 1
    p.save()
    assert order.items.first().product_name == "Test Runner"
    assert order.items.first().unit_price == 10000


def test_illegal_order_transition(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "fsm")
    with pytest.raises(ValidationError):
        s.transition(order, "delivered")


def test_reward_ledger_once(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    bag.user = get_user_model().objects.create_user(
        "reward@example.test", password="a-long-unique-password"
    )
    bag.save()
    order = s.create_checkout(bag, checkout_data, "reward")
    s.confirm_payment(order.reference, "reward1", "test", order.total, "KES")
    s.confirm_payment(order.reference, "reward1", "test", order.total, "KES")
    assert m.RewardEntry.objects.get().points == 100


def test_test_provider_disabled(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = False
    with pytest.raises(ValidationError):
        s.create_checkout(bag, checkout_data, "off")


def test_no_stripe_credentials_fails_before_reserving(bag, stock, checkout_data, settings):
    settings.STRIPE_SECRET_KEY = ""
    with pytest.raises(ValidationError):
        s.create_checkout(bag, {**checkout_data, "payment_provider": "stripe"}, "no-key")
    stock.refresh_from_db()
    assert stock.reserved == 0


def test_csv_preview_and_atomic_rollback(stock, tmp_path):
    file = tmp_path / "stock.csv"
    file.write_text("sku,location,on_hand\nTEST-BLACK-42,warehouse,9\n")
    call_command("import_inventory", str(file), stdout=StringIO())
    stock.refresh_from_db()
    assert stock.on_hand == 5
    call_command("import_inventory", str(file), apply=True, stdout=StringIO())
    stock.refresh_from_db()
    assert stock.on_hand == 9


@pytest.mark.django_db(transaction=True)
def test_two_buyers_compete_for_final_sku(stock, checkout_data, settings):
    assert connection.vendor == "postgresql", "This guarantee must run against PostgreSQL."
    settings.TEST_PAYMENTS = True
    stock.on_hand = 1
    stock.save()
    carts = []
    for _ in range(2):
        bag = m.Cart.objects.create()
        m.CartItem.objects.create(cart=bag, variant_size=stock.variant_size, quantity=1)
        carts.append(bag.pk)
    barrier = Barrier(2)

    def buy(cart_id):
        close_old_connections()
        try:
            bag = m.Cart.objects.get(pk=cart_id)
            barrier.wait(timeout=10)
            try:
                return s.create_checkout(bag, checkout_data, str(cart_id)).status
            except ValidationError:
                return "unavailable"
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(buy, carts))
    assert sorted(results) == ["payment_pending", "unavailable"]
    stock.refresh_from_db()
    assert (stock.on_hand, stock.reserved) == (1, 1)
