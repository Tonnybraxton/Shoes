from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from time import monotonic
from types import SimpleNamespace

import pytest
import stripe
from django.db import close_old_connections, connection, connections, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from shop import models as m
from shop import services as s


pytestmark = pytest.mark.django_db


def client_for_bag(bag):
    client = APIClient()
    session = client.session
    session["cart_id"] = str(bag.pk)
    session.save()
    return client


def test_stripe_expiry_allows_provider_latency_and_retry(bag, checkout_data, settings, monkeypatch):
    settings.STRIPE_SECRET_KEY = "sk_test_local_mock"
    attempts = []

    def create_session(**kwargs):
        attempts.append(kwargs)
        assert kwargs["line_items"][0]["price_data"]["unit_amount"] == 1035000
        assert kwargs["expires_at"] > int(timezone.now().timestamp()) + 30 * 60 + 10
        if len(attempts) == 1:
            raise stripe.APIConnectionError("Simulated ambiguous provider response")
        return SimpleNamespace(id="cs_test_retry", url="https://checkout.stripe.com/test")

    monkeypatch.setattr(stripe.checkout.Session, "create", create_session)
    data = {**checkout_data, "payment_provider": "stripe"}
    with pytest.raises(ValidationError, match="unavailable"):
        s.create_checkout(bag, data, "stripe-retry")
    order = s.create_checkout(bag, data, "stripe-retry")
    assert order.payment_session == "cs_test_retry"
    assert attempts[0] == attempts[1]
    assert m.Order.objects.count() == 1
    assert m.Reservation.objects.count() == 1


def test_expired_stripe_replay_does_not_create_payment_session(
    bag, checkout_data, settings, monkeypatch
):
    settings.STRIPE_SECRET_KEY = "sk_test_local_mock"
    data = {**checkout_data, "payment_provider": "stripe"}
    order = s.reserve_checkout(bag, data, "expired-stripe")
    m.Order.objects.filter(pk=order.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
    s.expire_order(order.pk)

    def unexpected_session(**kwargs):
        pytest.fail("An expired order must never create a payable session")

    monkeypatch.setattr(stripe.checkout.Session, "create", unexpected_session)
    assert s.create_checkout(bag, data, "expired-stripe").status == "cancelled"


def test_payment_event_cannot_acknowledge_a_different_order(bag, stock, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    first = s.create_checkout(bag, checkout_data, "first-event-owner")
    s.confirm_payment(first.reference, "same-event", "test", first.total, first.currency)
    another_bag = m.Cart.objects.create()
    m.CartItem.objects.create(cart=another_bag, variant_size=stock.variant_size, quantity=1)
    second = s.create_checkout(another_bag, checkout_data, "second-event-owner")
    with pytest.raises(ValidationError, match="another order"):
        s.confirm_payment(second.reference, "same-event", "test", second.total, second.currency)
    second.refresh_from_db()
    stock.refresh_from_db()
    assert second.status == "payment_pending"
    assert (stock.on_hand, stock.reserved) == (4, 1)
    assert m.PaymentEvent.objects.get().order_id == first.pk


@pytest.mark.parametrize("damage", ["delete", "release"])
def test_incomplete_reservation_never_marks_an_order_paid(
    bag, stock, checkout_data, settings, damage
):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "incomplete-reservation")
    if damage == "delete":
        order.reservations.all().delete()
    else:
        order.reservations.update(released=True)
    with pytest.raises(ValidationError, match="reservation is incomplete"):
        s.confirm_payment(order.reference, "incomplete", "test", order.total, order.currency)
    order.refresh_from_db()
    stock.refresh_from_db()
    assert order.status == "payment_pending"
    assert order.paid_at is None
    assert (stock.on_hand, stock.reserved) == (5, 1)
    assert not m.PaymentEvent.objects.exists()


def test_test_payment_requires_the_checkout_session(bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "private-test-order")
    intruder = APIClient()
    response = intruder.post(
        "/api/v1/payments/test/complete/", {"reference": str(order.reference)}, format="json"
    )
    assert response.status_code == 404
    order.refresh_from_db()
    assert order.status == "payment_pending"
    assert not m.PaymentEvent.objects.exists()


def wait_for_database_lock(worker_pid):
    deadline = monotonic() + 5
    pause = Event()
    while monotonic() < deadline:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT wait_event_type FROM pg_stat_activity WHERE pid = %s", [worker_pid]
            )
            row = cursor.fetchone()
        if row and row[0] == "Lock":
            return
        pause.wait(0.02)
    pytest.fail("Concurrent operation did not wait for its database lock")


def worker_connection(action, ready, worker_pid):
    close_old_connections()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid()")
            worker_pid.append(cursor.fetchone()[0])
        ready.set()
        return action()
    finally:
        connections.close_all()


@pytest.mark.django_db(transaction=True)
def test_expiration_and_checkout_use_consistent_lock_order(bag, stock, checkout_data, settings):
    assert connection.vendor == "postgresql"
    settings.TEST_PAYMENTS = True
    promo = m.Promotion.objects.create(
        code="LOCKS", name="Concurrent promotion", kind="percent", value=10, per_user_limit=2
    )
    bag.promo_code = promo.code
    bag.save(update_fields=["promo_code"])
    expired = s.create_checkout(bag, checkout_data, "expiring")
    m.Order.objects.filter(pk=expired.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
    other_bag = m.Cart.objects.create(promo_code=promo.code)
    m.CartItem.objects.create(cart=other_bag, variant_size=stock.variant_size, quantity=1)
    ready, worker_pid = Event(), []
    with ThreadPoolExecutor(max_workers=1) as pool:
        with transaction.atomic():
            m.Promotion.objects.select_for_update().get(pk=promo.pk)
            expiry = pool.submit(
                worker_connection, lambda: s.expire_order(expired.pk), ready, worker_pid
            )
            assert ready.wait(5)
            wait_for_database_lock(worker_pid[0])
            # Expiry must wait on the promotion before taking stock that checkout needs.
            current = s.create_checkout(other_bag, checkout_data, "replacement")
        assert expiry.result(timeout=10)
    stock.refresh_from_db()
    promo.refresh_from_db()
    assert current.status == "payment_pending"
    assert (stock.on_hand, stock.reserved) == (5, 1)
    assert promo.uses == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("method", ["patch", "delete"])
def test_cart_edits_serialize_with_payment_cleanup(bag, checkout_data, settings, method):
    assert connection.vendor == "postgresql"
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "concurrent-edit")
    item_id = bag.items.get().pk
    owner = client_for_bag(bag)
    ready, worker_pid = Event(), []

    def edit():
        return getattr(owner, method)(
            f"/api/v1/cart/items/{item_id}/", {"quantity": 2}, format="json"
        )

    with ThreadPoolExecutor(max_workers=1) as pool:
        with transaction.atomic():
            m.Cart.objects.select_for_update().get(pk=bag.pk)
            change = pool.submit(worker_connection, edit, ready, worker_pid)
            assert ready.wait(5)
            wait_for_database_lock(worker_pid[0])
            s.confirm_payment(
                order.reference, "concurrent-paid", "test", order.total, order.currency
            )
        assert change.result(timeout=10).status_code == 404
    assert not bag.items.exists()
