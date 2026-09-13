import hashlib
import json
from collections import Counter
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import (
    Product,
    VariantSize,
    Inventory,
    SiteSettings,
    Cart,
    Promotion,
    Order,
    OrderItem,
    Reservation,
    OrderHistory,
    PaymentEvent,
    RewardEntry,
    Outbox,
)

ZERO = Decimal("0.00")


def live(qs):
    now = timezone.now()
    return (
        qs.filter(active=True)
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gt=now))
    )


def published():
    now = timezone.now()
    return (
        Product.objects.filter(
            active=True, status="published", brand__active=True, category__active=True
        )
        .filter(Q(visible_from__isnull=True) | Q(visible_from__lte=now))
        .filter(Q(visible_until__isnull=True) | Q(visible_until__gt=now))
    )


def catalog():
    return (
        published()
        .select_related("brand", "category")
        .prefetch_related(
            "variants__images",
            "variants__sizes__size",
            "variants__sizes__inventory__location",
            "merch_badges",
        )
    )


def store_settings():
    return SiteSettings.objects.first() or SiteSettings()


def available(sku):
    return sum(
        i.available for i in sku.inventory.all() if i.location.active and not i.location.is_store
    )


def sellable(sku):
    now = timezone.now()
    return (
        sku.variant.active
        and published().filter(pk=sku.variant.product_id).exists()
        and (sku.variant.release_at is None or sku.variant.release_at <= now)
        and (sku.variant.product.release_at is None or sku.variant.product.release_at <= now)
    )


def first_image(variant):
    image = next(iter(variant.images.all()), None)
    return image.image.url if image else ""


def money(value):
    return str(Decimal(value).quantize(Decimal(".01")))


def cart_for(request):
    cart_id = request.session.get("cart_id")
    cart = Cart.objects.filter(pk=cart_id).first() if cart_id else None
    if (
        cart
        and cart.user_id
        and (not request.user.is_authenticated or cart.user_id != request.user.id)
    ):
        cart = None
    if not cart:
        cart = Cart.objects.create(user=request.user if request.user.is_authenticated else None)
        request.session["cart_id"] = str(cart.id)
    elif request.user.is_authenticated and not cart.user_id:
        cart.user = request.user
        cart.save(update_fields=["user"])
    return cart


def cart_rows(cart):
    return cart.items.select_related(
        "variant_size__variant__product__brand", "variant_size__size"
    ).prefetch_related("variant_size__inventory__location", "variant_size__variant__images")


def price_cart(cart, strict=False, email=""):
    config = store_settings()
    items = []
    eligible = []
    for item in cart_rows(cart):
        sku = item.variant_size
        variant = sku.variant
        product = variant.product
        stock = available(sku) if sellable(sku) else 0
        if strict and item.quantity > stock:
            raise ValidationError(f"{product.name}, {sku.size}: requested quantity is unavailable.")
        amount = variant.effective_price * item.quantity
        items.append(
            {
                "id": item.id,
                "quantity": item.quantity,
                "variant_size_id": sku.id,
                "product_slug": product.slug,
                "product_name": product.name,
                "brand": product.brand.name,
                "color_name": variant.color_name,
                "size_label": str(sku.size),
                "image": first_image(variant),
                "unit_price": money(variant.effective_price),
                "line_total": money(amount),
                "available": stock,
            }
        )
        eligible.append((product, amount))
    subtotal = sum((Decimal(i["line_total"]) for i in items), ZERO)
    discount = ZERO
    shipping = (
        ZERO
        if not items
        or subtotal >= config.free_shipping_threshold
        or all(p.free_shipping for p, _ in eligible)
        else config.standard_shipping
    )
    promotion = None
    candidates = live(Promotion.objects.all())
    if cart.promo_code:
        candidates = candidates.filter(code__iexact=cart.promo_code)
    else:
        candidates = candidates.filter(automatic=True)
    for promo in candidates:
        if (
            promo.uses >= promo.usage_limit
            or subtotal < promo.minimum
            or (promo.members_only and not cart.user_id)
        ):
            continue
        prior = Order.objects.filter(promo_code=promo.code).exclude(
            status__in=["cancelled", "refunded"]
        )
        prior = (
            prior.filter(user_id=cart.user_id)
            if cart.user_id
            else prior.filter(email__iexact=email)
            if email
            else prior.none()
        )
        if prior.count() >= promo.per_user_limit:
            continue
        product_ids = set(promo.products.values_list("id", flat=True))
        brand_ids = set(promo.brands.values_list("id", flat=True))
        category_ids = set(promo.categories.values_list("id", flat=True))
        base = sum(
            (
                amount
                for p, amount in eligible
                if p.promo_eligible
                and (not product_ids or p.id in product_ids)
                and (not brand_ids or p.brand_id in brand_ids)
                and (not category_ids or p.category_id in category_ids)
            ),
            ZERO,
        )
        if not base:
            continue
        discount = (
            min(base, (base * min(promo.value, 100) / 100).quantize(Decimal(".01")))
            if promo.kind == "percent"
            else min(base, promo.value)
            if promo.kind == "fixed"
            else ZERO
        )
        if promo.kind == "shipping":
            shipping = ZERO
        promotion = promo
        break
    if strict and cart.promo_code and not promotion:
        raise ValidationError("This promotion is not eligible for this order.")
    return {
        "id": str(cart.id),
        "items": items,
        "subtotal": money(subtotal),
        "discount": money(discount),
        "shipping": money(shipping),
        "total": money(subtotal - discount + shipping),
        "currency": settings.CURRENCY,
        "promo_code": promotion.code if promotion else "",
        "free_shipping_remaining": money(max(ZERO, config.free_shipping_threshold - subtotal)),
    }


TRANSITIONS = {
    "pending": {"payment_pending", "cancelled"},
    "payment_pending": {"paid", "cancelled"},
    "paid": {"processing", "refund_pending"},
    "processing": {"packed", "refund_pending"},
    "packed": {"shipped", "ready_pickup", "refund_pending"},
    "shipped": {"delivered"},
    "ready_pickup": {"delivered"},
    "delivered": {"return_requested"},
    "return_requested": {"returned", "delivered"},
    "returned": {"refund_pending"},
    "refund_pending": {"refunded"},
    "refunded": set(),
    "cancelled": set(),
}


def transition(order, target, note=""):
    if target not in TRANSITIONS.get(order.status, set()):
        raise ValidationError(f"Cannot change {order.status} to {target}.")
    order.status = target
    order.save(update_fields=["status"])
    OrderHistory.objects.create(order=order, status=target, note=note)
    if target in {"paid", "shipped", "ready_pickup", "delivered", "return_requested", "refunded"}:
        Outbox.objects.get_or_create(
            dedupe_key=f"order:{order.reference}:{target}",
            defaults={
                "kind": target,
                "recipient": order.email,
                "subject": f"Your SOLELINE order: {target.replace('_', ' ')}",
                "body": f"Order {order.reference} is {target.replace('_', ' ')}. Track it securely: {settings.SITE_URL}/orders/{order.reference}?token={tracking_token(order)}",
            },
        )


def tracking_token(order):
    return signing.dumps(str(order.reference), salt="guest-order")


def authorize_order(request, order, token=None):
    if request.user.is_authenticated and order.user_id == request.user.id:
        return True
    try:
        return signing.loads(token or "", salt="guest-order", max_age=60 * 60 * 24 * 90) == str(
            order.reference
        )
    except signing.BadSignature:
        return False


@transaction.atomic
def reserve_checkout(cart, data, key):
    if not key or len(key) > 100:
        raise ValidationError("A valid Idempotency-Key is required.")
    cart = Cart.objects.select_for_update().get(pk=cart.pk)
    digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    prior = Order.objects.filter(cart=cart, idempotency_key=key).first()
    if prior:
        if prior.request_hash != digest:
            raise ValidationError("Idempotency key was already used for another request.")
        return prior
    if Order.objects.filter(
        cart=cart, status="payment_pending", expires_at__gt=timezone.now()
    ).exists():
        raise ValidationError(
            "A payment is already pending for this bag. Complete it or wait for its reservation to expire."
        )
    provider = data["payment_provider"]
    if provider == "test" and not settings.TEST_PAYMENTS:
        raise ValidationError("Test payments are disabled.")
    if provider == "stripe" and not settings.STRIPE_SECRET_KEY:
        raise ValidationError("Payments are not configured yet.")
    if provider not in {"stripe", "test"}:
        raise ValidationError("Unsupported payment provider.")
    # Lock promotions before counting redemptions across separate carts.
    if cart.promo_code:
        list(Promotion.objects.select_for_update().filter(code__iexact=cart.promo_code))
    else:
        list(Promotion.objects.select_for_update().filter(automatic=True).order_by("pk"))
    priced = price_cart(cart, strict=True, email=data["email"])
    if not priced["items"]:
        raise ValidationError("Your bag is empty.")
    skus = {
        s.id: s
        for s in VariantSize.objects.filter(
            id__in=[i["variant_size_id"] for i in priced["items"]]
        ).select_related("variant__product", "size")
    }
    inventory = list(
        Inventory.objects.select_for_update()
        .filter(variant_size_id__in=skus, location__active=True, location__is_store=False)
        .order_by("id")
    )
    for item in priced["items"]:
        if (
            sum(i.available for i in inventory if i.variant_size_id == item["variant_size_id"])
            < item["quantity"]
        ):
            raise ValidationError("Stock changed. Please review your bag.")
    order = Order.objects.create(
        cart=cart,
        user=cart.user,
        idempotency_key=key,
        request_hash=digest,
        email=data["email"].lower(),
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        address=data["address"],
        subtotal=Decimal(priced["subtotal"]),
        discount=Decimal(priced["discount"]),
        shipping=Decimal(priced["shipping"]),
        total=Decimal(priced["total"]),
        currency=settings.CURRENCY,
        promo_code=priced["promo_code"],
        payment_provider=provider,
        # Stripe requires at least 30 minutes from provider-side session creation.
        # Allow request latency/retries while keeping the provider and stock expiry equal.
        expires_at=timezone.now() + timedelta(minutes=35 if provider == "stripe" else 30),
    )
    for item in priced["items"]:
        sku = skus[item["variant_size_id"]]
        OrderItem.objects.create(
            order=order,
            variant_size=sku,
            sku=sku.sku,
            **{
                k: item[k]
                for k in [
                    "product_name",
                    "product_slug",
                    "brand",
                    "color_name",
                    "size_label",
                    "image",
                    "quantity",
                    "unit_price",
                    "line_total",
                ]
            },
        )
        remaining = item["quantity"]
        for stock in inventory:
            if stock.variant_size_id != sku.id or remaining == 0:
                continue
            amount = min(stock.available, remaining)
            if amount:
                stock.reserved += amount
                stock.save(update_fields=["reserved"])
                Reservation.objects.create(order=order, inventory=stock, quantity=amount)
                remaining -= amount
    if order.promo_code:
        Promotion.objects.filter(code=order.promo_code).update(uses=F("uses") + 1)
    transition(order, "payment_pending")
    return order


def create_checkout(cart, data, key):
    # Commit the reservation before contacting a provider. An ambiguous network result
    # retains the order and stable provider idempotency key, allowing a safe retry.
    order = reserve_checkout(cart, data, key)
    # Provider request uses stable idempotency to safely retry upstream.
    if (
        order.payment_provider == "stripe"
        and not order.payment_session
        and order.status == "payment_pending"
        and order.expires_at > timezone.now()
    ):
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                customer_email=order.email,
                line_items=[
                    {
                        "price_data": {
                            "currency": order.currency.lower(),
                            "product_data": {"name": f"SOLELINE order {order.reference}"},
                            "unit_amount": int(order.total * 100),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={"order_reference": str(order.reference)},
                success_url=f"{settings.SITE_URL}/orders/{order.reference}?token={tracking_token(order)}",
                cancel_url=f"{settings.SITE_URL}/cart",
                expires_at=int(order.expires_at.timestamp()),
                idempotency_key=f"checkout-{order.reference}",
            )
            order.payment_session = session.id
            order.payment_url = session.url
            order.save(update_fields=["payment_session", "payment_url"])
        except stripe.StripeError as exc:
            raise ValidationError("Payment provider is unavailable; please try again.") from exc
    return order


@transaction.atomic
def confirm_payment(reference, event_id, provider, amount, currency, session_id=""):
    lookup = Order.objects.only("cart_id").get(reference=reference)
    # Checkout and every bag mutation take this lock first. Payment cleanup must use
    # the same order so concurrent edits cannot be lost or recreate purchased lines.
    Cart.objects.select_for_update().get(pk=lookup.cart_id)
    order = Order.objects.select_for_update().get(pk=lookup.pk)
    if (
        order.payment_provider != provider
        or Decimal(amount) != order.total
        or currency.upper() != order.currency
    ):
        raise ValidationError("Payment verification failed.")
    if provider == "stripe" and order.payment_session != session_id:
        raise ValidationError("Payment session mismatch.")
    event = PaymentEvent.objects.filter(event_id=event_id).first()
    if event:
        if event.order_id != order.pk or event.provider != provider:
            raise ValidationError("Payment event was already used for another order.")
        return order
    if order.paid_at:
        return order
    if order.status != "payment_pending" or order.expires_at <= timezone.now():
        # Late charges need operator reconciliation/refund, never fulfillment without stock.
        raise ValidationError("Order reservation expired; payment requires reconciliation.")
    reservations = list(
        order.reservations.filter(released=False)
        .select_related("inventory")
        .order_by("inventory_id")
    )
    stocks = {
        s.id: s
        for s in Inventory.objects.select_for_update()
        .filter(id__in=[r.inventory_id for r in reservations])
        .order_by("id")
    }
    required = Counter()
    for item in order.items.all():
        required[item.variant_size_id] += item.quantity
    reserved = Counter()
    for reservation in reservations:
        stock = stocks[reservation.inventory_id]
        reserved[stock.variant_size_id] += reservation.quantity
    if not required or reserved != required:
        raise ValidationError("Order reservation is incomplete; payment requires reconciliation.")
    for reservation in reservations:
        stock = stocks[reservation.inventory_id]
        stock.reserved -= reservation.quantity
        stock.on_hand -= reservation.quantity
        stock.save(update_fields=["reserved", "on_hand"])
        reservation.released = True
        reservation.save(update_fields=["released"])
    PaymentEvent.objects.create(provider=provider, event_id=event_id, order=order)
    order.paid_at = timezone.now()
    order.save(update_fields=["paid_at"])
    transition(order, "paid", "Verified payment event")
    # Clear only the purchased lines/quantities; preserve edits made after checkout.
    for purchased in order.items.all():
        item = order.cart.items.filter(variant_size=purchased.variant_size).first()
        if item:
            if item.quantity <= purchased.quantity:
                item.delete()
            else:
                item.quantity -= purchased.quantity
                item.save(update_fields=["quantity"])
    config = store_settings()
    if order.user_id and config.rewards_enabled:
        RewardEntry.objects.get_or_create(
            dedupe_key=f"purchase:{order.reference}",
            defaults={
                "user_id": order.user_id,
                "order": order,
                "points": int((order.subtotal - order.discount) / 100) * config.points_per_100,
                "reason": "Purchase",
                "expires_at": timezone.now() + timedelta(days=365),
            },
        )
    return order


@transaction.atomic
def expire_order(order_id):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status != "payment_pending" or order.expires_at > timezone.now():
        return False
    # Match checkout's promotion-before-inventory ordering to avoid deadlocks
    # when another cart redeems this promotion while expired stock is released.
    if order.promo_code:
        list(Promotion.objects.select_for_update().filter(code=order.promo_code))
    for reservation in order.reservations.filter(released=False).order_by("inventory_id"):
        stock = Inventory.objects.select_for_update().get(pk=reservation.inventory_id)
        stock.reserved -= reservation.quantity
        stock.save(update_fields=["reserved"])
        reservation.released = True
        reservation.save(update_fields=["released"])
    if order.promo_code:
        Promotion.objects.filter(code=order.promo_code, uses__gt=0).update(uses=F("uses") - 1)
    transition(order, "cancelled", "Payment reservation expired")
    return True
