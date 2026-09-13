from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import transaction, connection
from django.db.models import Q, F, Sum, Count, Min, Max
from django.http import Http404
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, throttle_classes, authentication_classes
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import exception_handler as drf_exception_handler
from . import models as m
from . import services as s
from .serializers import (
    product_data,
    order_data,
    CheckoutSerializer,
    AddressSerializer,
    ReviewSerializer,
)


def exception_handler(exc, context):
    if isinstance(exc, (DjangoValidationError, ValueError, InvalidOperation)):
        exc = ValidationError("Invalid input.")
    response = drf_exception_handler(exc, context)
    if response is not None:
        fields = response.data
        detail = (
            fields.get("detail")
            if isinstance(fields, dict)
            else fields[0]
            if isinstance(fields, list) and fields
            else "Request could not be completed."
        )
        response.data = {
            "error": {
                "code": getattr(exc, "default_code", "request_error"),
                "message": str(detail or "Check the submitted fields."),
                "fields": fields,
            }
        }
    return response


def require_user(request):
    if not request.user.is_authenticated:
        raise NotAuthenticated()


def csrf(request):
    SessionAuthentication().enforce_csrf(request)


def session_data(request):
    u = request.user
    return {
        "user": {"id": u.id, "email": u.email, "first_name": u.first_name}
        if u.is_authenticated
        else None,
        "csrf_token": get_token(request),
    }


class AuthThrottle(AnonRateThrottle):
    scope = "auth"


def paginate(request, queryset, render=lambda x: x):
    try:
        page = max(1, int(request.query_params.get("page", 1)))
    except ValueError:
        raise ValidationError("Invalid page.")
    count = queryset.count() if hasattr(queryset, "model") else len(queryset)
    offset = (page - 1) * 24
    query = request.query_params.copy()

    def page_url(number):
        query["page"] = number
        return request.path + "?" + query.urlencode()

    return {
        "count": count,
        "next": page_url(page + 1) if offset + 24 < count else None,
        "previous": page_url(page - 1) if page > 1 else None,
        "results": [render(x) for x in queryset[offset : offset + 24]],
    }


def named_data(obj):
    return {
        "id": obj.id,
        "name": obj.name,
        "slug": obj.slug,
        "description": obj.description,
        "image": obj.image.url if obj.image else "",
    }


def filter_products(request, qs):
    params = request.query_params
    if params.get("ids"):
        try:
            ids = [int(v) for v in params["ids"].split(",")[:100]]
        except ValueError:
            raise ValidationError("Invalid product IDs.")
        qs = qs.filter(id__in=ids)
    for key, field in {
        "brand": "brand__slug",
        "category": "category__slug",
        "collection": "collections__slug",
        "gender": "gender",
        "sport": "sport",
        "style": "style",
        "age": "age_group",
        "color": "variants__color_family",
        "size": "variants__sizes__size__label",
    }.items():
        if params.get(key):
            qs = qs.filter(**{field + "__in": params[key].split(",")[:20]})
    for key, field in {
        "new": "is_new",
        "best": "is_best_seller",
        "limited": "is_limited",
        "promo_eligible": "promo_eligible",
        "free_shipping": "free_shipping",
    }.items():
        if params.get(key) == "true":
            qs = qs.filter(**{field: True})
    if params.get("sale") == "true":
        qs = qs.filter(
            Q(compare_at_price__gt=F("base_price"))
            | Q(variants__compare_at_price__gt=F("variants__price"))
        )
    for key, lookup in [
        ("min_price", "base_price__gte"),
        ("max_price", "base_price__lte"),
        ("rating", "rating_cached__gte"),
    ]:
        if params.get(key):
            try:
                value = Decimal(params[key])
            except InvalidOperation:
                raise ValidationError("Invalid numeric filter.")
            if not value.is_finite() or value < 0:
                raise ValidationError("Invalid numeric filter.")
            qs = qs.filter(**{lookup: value})
    if params.get("in_stock") == "true":
        qs = qs.filter(
            variants__active=True,
            variants__sizes__inventory__on_hand__gt=F("variants__sizes__inventory__reserved"),
        )
    search = params.get("search", "").strip()[:100]
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(model_family__icontains=search)
            | Q(variants__sku__icontains=search)
            | Q(variants__color_name__icontains=search)
        )
    sort = {
        "featured": "sort_order",
        "newest": "-created_at",
        "bestselling": "-is_best_seller",
        "rating": "-rating_cached",
        "price_asc": "base_price",
        "price_desc": "-base_price",
        "name": "name",
    }.get(params.get("sort"), "sort_order")
    return qs.order_by(sort, "id").distinct()


@api_view(["GET"])
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return Response({"status": "ok", "database": "ok"})


@api_view(["GET"])
def session(request):
    return Response(session_data(request))


@api_view(["GET"])
def site(request):
    config = s.store_settings()

    def nav(n):
        return {
            "label": n.label,
            "href": n.href,
            "children": [nav(c) for c in s.live(n.children.all())],
        }

    sections = []
    for section in s.live(m.PageSection.objects.prefetch_related("products")):
        data = {
            k: getattr(section, k)
            for k in ["id", "type", "title", "subtitle", "body", "href", "cta", "settings"]
        }
        data["image"] = section.image.url if section.image else ""
        data["products"] = [
            product_data(p) for p in s.catalog().filter(pk__in=section.products.values("id"))[:8]
        ]
        sections.append(data)
    return Response(
        {
            "name": config.name,
            "tagline": config.tagline,
            "currency": settings.CURRENCY,
            "announcements": list(
                s.live(m.Announcement.objects.all()).values("id", "text", "href")
            ),
            "navigation": [nav(n) for n in s.live(m.Navigation.objects.filter(parent=None))],
            "sections": sections,
            "flags": {"pickup": False, "raffles": False, "gift_cards": False},
            "payment_enabled": bool(settings.STRIPE_SECRET_KEY),
            "test_payments": settings.TEST_PAYMENTS,
            "demo": config.demo,
            "footer": list(m.Policy.objects.values("slug", "title")),
        }
    )


@api_view(["GET"])
def products(request, slug=None):
    if slug:
        return Response(product_data(get_object_or_404(s.catalog(), slug=slug)))
    return Response(paginate(request, filter_products(request, s.catalog()), product_data))


@api_view(["GET"])
def related(request, slug):
    product = get_object_or_404(s.published(), slug=slug)
    return Response(
        paginate(
            request,
            s.catalog()
            .filter(Q(category=product.category) | Q(brand=product.brand))
            .exclude(pk=product.pk)[:8],
            product_data,
        )
    )


@api_view(["GET"])
def facets(request):
    qs = filter_products(request, s.published())
    return Response(
        {
            "brands": list(
                m.Brand.objects.filter(products__in=qs)
                .annotate(count=Count("products", distinct=True))
                .values("slug", "name", "count")
            ),
            "categories": list(
                m.Category.objects.filter(products__in=qs)
                .annotate(count=Count("products", distinct=True))
                .values("slug", "name", "count")
            ),
            "sizes": list(
                m.Size.objects.filter(variantsize__variant__product__in=qs)
                .annotate(count=Count("variantsize__variant__product", distinct=True))
                .values("id", "label", "system", "count")
            ),
            "colors": [
                {"name": v["color_family"], "code": v["code"], "count": v["count"]}
                for v in m.Variant.objects.filter(product__in=qs, active=True)
                .values("color_family")
                .annotate(code=Min("color_code"), count=Count("product", distinct=True))
            ],
            "genders": [
                {"value": v["gender"], "label": v["gender"].title(), "count": v["count"]}
                for v in qs.values("gender")
                .order_by("gender")
                .annotate(count=Count("id", distinct=True))
            ],
            "price": qs.aggregate(min=Min("base_price"), max=Max("base_price")),
        }
    )


@api_view(["GET"])
def search(request):
    q = request.query_params.get("q", "").strip()[:100]
    if len(q) < 2:
        return Response({"products": [], "brands": [], "categories": [], "suggestions": []})
    qs = (
        s.catalog()
        .filter(
            Q(name__icontains=q)
            | Q(brand__name__icontains=q)
            | Q(model_family__icontains=q)
            | Q(variants__sku__icontains=q)
            | Q(variants__color_name__icontains=q)
        )
        .distinct()[:6]
    )
    return Response(
        {
            "products": [product_data(p) for p in qs],
            "brands": [
                named_data(b) for b in m.Brand.objects.filter(active=True, name__icontains=q)[:4]
            ],
            "categories": [
                named_data(c) for c in m.Category.objects.filter(active=True, name__icontains=q)[:4]
            ],
            "suggestions": list(
                s.published().filter(name__icontains=q).values_list("name", flat=True)[:4]
            ),
        }
    )


@api_view(["GET"])
def directory(request, kind):
    model = {"brands": m.Brand, "collections": m.Collection, "stores": m.Location}.get(kind)
    if model is None:
        raise Http404
    qs = model.objects.filter(active=True)
    if kind == "stores":
        qs = qs.none()
    if kind == "collections":
        qs = s.live(qs)
    return Response(paginate(request, qs, named_data))


@api_view(["GET"])
def releases(request, slug=None):
    qs = (
        m.Release.objects.filter(active=True)
        .select_related("product__brand")
        .order_by("release_at")
    )
    if request.query_params.get("status") == "upcoming":
        qs = qs.filter(release_at__gt=timezone.now())
    if request.query_params.get("status") == "released":
        qs = qs.filter(release_at__lte=timezone.now())
    if request.query_params.get("brand"):
        qs = qs.filter(product__brand__slug=request.query_params["brand"])

    def render(r):
        return {
            **named_data(r),
            "title": r.name,
            "release_at": r.release_at,
            "status": "soldout"
            if r.sold_out
            else "upcoming"
            if r.release_at > timezone.now()
            else "released",
            "product": product_data(s.catalog().get(pk=r.product_id))
            if r.product_id and s.published().filter(pk=r.product_id).exists()
            else None,
            "server_time": timezone.now(),
        }

    return Response(
        render(get_object_or_404(qs, slug=slug)) if slug else paginate(request, qs, render)
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@transaction.atomic
def cart(request, item_id=None, action=None):
    if request.method != "GET":
        csrf(request)
    bag = s.cart_for(request)
    if request.method != "GET":
        bag = m.Cart.objects.select_for_update().get(pk=bag.pk)
    if action == "promo":
        code = (
            str(request.data.get("code", "")).strip().upper()[:40]
            if request.method == "POST"
            else ""
        )
        if code and not s.live(m.Promotion.objects.filter(code__iexact=code)).exists():
            raise ValidationError("Promotion code is invalid or expired.")
        bag.promo_code = code
        bag.save(update_fields=["promo_code"])
    elif request.method == "POST":
        sku = get_object_or_404(
            m.VariantSize.objects.select_related("variant__product", "size").prefetch_related(
                "inventory__location"
            ),
            pk=request.data.get("variant_size_id"),
        )
        quantity = serializers.IntegerField(min_value=1, max_value=10).run_validation(
            request.data.get("quantity")
        )
        item = bag.items.filter(variant_size=sku).first()
        total = quantity + (item.quantity if item else 0)
        if not s.sellable(sku) or total > s.available(sku) or total > 10:
            raise ValidationError("This size or quantity is unavailable.")
        if item:
            item.quantity = total
            item.save(update_fields=["quantity"])
        else:
            m.CartItem.objects.create(cart=bag, variant_size=sku, quantity=quantity)
    elif request.method in {"PATCH", "DELETE"}:
        item = get_object_or_404(bag.items, id=item_id)
        if request.method == "DELETE":
            item.delete()
        else:
            quantity = serializers.IntegerField(min_value=1, max_value=10).run_validation(
                request.data.get("quantity")
            )
            if quantity > s.available(item.variant_size):
                raise ValidationError("Requested quantity is unavailable.")
            item.quantity = quantity
            item.save(update_fields=["quantity"])
    return Response(s.price_cart(bag))


@api_view(["POST"])
def checkout(request):
    csrf(request)
    form = CheckoutSerializer(data=request.data)
    form.is_valid(raise_exception=True)
    order = s.create_checkout(
        s.cart_for(request), form.validated_data, request.headers.get("Idempotency-Key", "")
    )
    return Response(
        {
            "order": {**order_data(order), "tracking_token": s.tracking_token(order)},
            "payment": {
                "provider": order.payment_provider,
                "redirect_url": order.payment_url,
                "client_secret": None,
            },
            "test_mode": order.payment_provider == "test",
        },
        status=201,
    )


@api_view(["POST"])
def test_complete(request):
    csrf(request)
    if not settings.TEST_PAYMENTS:
        raise Http404
    order = get_object_or_404(
        m.Order, reference=request.data.get("reference"), cart=s.cart_for(request)
    )
    order = s.confirm_payment(
        order.reference, f"test:{order.reference}", "test", order.total, order.currency
    )
    return Response(order_data(order))


@api_view(["POST"])
@authentication_classes([])
def stripe_webhook(request):
    import stripe

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise Http404
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise ValidationError("Invalid webhook signature.")
    if event["type"] in ["checkout.session.completed", "checkout.session.async_payment_succeeded"]:
        obj = event["data"]["object"]
        if obj["payment_status"] == "paid":
            s.confirm_payment(
                obj["metadata"]["order_reference"],
                event["id"],
                "stripe",
                Decimal(obj["amount_total"]) / 100,
                obj["currency"],
                obj["id"],
            )
    return Response({"received": True})


@api_view(["GET", "POST"])
def orders(request, reference=None):
    if request.method == "POST":
        csrf(request)
        reference = request.data.get("reference")
    if reference:
        order = get_object_or_404(m.Order, reference=reference)
        token = (
            request.data.get("token")
            if request.method == "POST"
            else request.query_params.get("token")
        )
        if not s.authorize_order(request, order, token):
            raise Http404
        return Response(order_data(order))
    require_user(request)
    return Response(paginate(request, m.Order.objects.filter(user=request.user), order_data))


@api_view(["POST"])
@throttle_classes([AuthThrottle])
def auth(request, action):
    csrf(request)
    User = get_user_model()
    if action == "logout":
        logout(request)
        return Response(session_data(request))
    email = str(request.data.get("email", "")).lower().strip()
    if action in {"register", "login", "password-reset"}:
        try:
            validate_email(email)
        except DjangoValidationError:
            raise ValidationError("Enter a valid email address.")
    if action == "register":
        password = request.data.get("password", "")
        user = User(
            username=email,
            email=email,
            first_name=str(request.data.get("first_name", ""))[:100],
            last_name=str(request.data.get("last_name", ""))[:100],
        )
        try:
            validate_password(password, user)
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages})
        if User.objects.filter(username=email).exists():
            raise ValidationError(
                "An account with these details cannot be created. Try signing in or resetting your password."
            )
        user.set_password(password)
        user.save()
        m.Profile.objects.create(user=user)
        login(request, user)
        token = signing.dumps(user.id, salt="verify-email")
        m.Outbox.objects.create(
            kind="welcome",
            recipient=email,
            subject="Welcome to SOLELINE",
            body=f"Confirm your email: {settings.SITE_URL}/account/verify?token={token}",
            dedupe_key=f"welcome:{user.id}",
        )
        return Response(session_data(request), status=201)
    if action == "login":
        user = authenticate(request, username=email, password=request.data.get("password", ""))
        if not user:
            raise ValidationError("Email or password is incorrect.")
        login(request, user)
        return Response(session_data(request))
    if action == "password-reset":
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            m.Outbox.objects.get_or_create(
                dedupe_key=f"reset:{user.id}:{token}",
                defaults={
                    "kind": "reset",
                    "recipient": email,
                    "subject": "Reset your SOLELINE password",
                    "body": f"{settings.SITE_URL}/account/reset?uid={uid}&token={token}",
                },
            )
        return Response({"message": "If an account exists, a reset link will be sent."})
    if action == "password-reset-confirm":
        try:
            user = User.objects.get(
                pk=force_str(urlsafe_base64_decode(request.data.get("uid", "")))
            )
        except (ValueError, User.DoesNotExist):
            raise ValidationError("Reset link is invalid.")
        if not default_token_generator.check_token(user, request.data.get("token", "")):
            raise ValidationError("Reset link expired or is invalid.")
        try:
            validate_password(request.data.get("password", ""), user)
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages})
        user.set_password(request.data["password"])
        user.save()
        return Response({"message": "Password updated. You can now sign in."})
    if action == "verify":
        try:
            uid = signing.loads(request.data.get("token", ""), salt="verify-email", max_age=86400)
        except signing.BadSignature:
            raise ValidationError("Verification link expired or is invalid.")
        m.Profile.objects.filter(user_id=uid).update(email_verified=True)
        return Response({"message": "Email verified."})
    raise Http404


@api_view(["GET", "PATCH"])
def account(request):
    require_user(request)
    profile, _ = m.Profile.objects.get_or_create(user=request.user)
    if request.method == "PATCH":
        csrf(request)
        for key in ["first_name", "last_name"]:
            if key in request.data:
                setattr(request.user, key, str(request.data[key])[:100])
        request.user.save()
        for key in ["phone", "usual_size", "size_system", "fit_preference"]:
            if key in request.data:
                setattr(profile, key, str(request.data[key])[:20])
        profile.save()
    return Response(
        {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            **{
                key: getattr(profile, key)
                for key in [
                    "phone",
                    "usual_size",
                    "size_system",
                    "fit_preference",
                    "email_verified",
                ]
            },
        }
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
def addresses(request, pk=None):
    require_user(request)
    if request.method == "GET":
        return Response(
            paginate(request, request.user.addresses.all(), lambda a: AddressSerializer(a).data)
        )
    csrf(request)
    instance = get_object_or_404(request.user.addresses, pk=pk) if pk else None
    if request.method == "DELETE":
        instance.delete()
        return Response(status=204)
    form = AddressSerializer(instance, data=request.data, partial=request.method == "PATCH")
    form.is_valid(raise_exception=True)
    form.save(user=request.user)
    return Response(form.data)


@api_view(["GET", "POST", "DELETE"])
def wishlist(request, product_id=None, merge=False):
    require_user(request)
    if request.method != "GET":
        csrf(request)
        if request.method == "DELETE":
            m.Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        else:
            ids = request.data.get("product_ids", []) if merge else [request.data.get("product_id")]
            if not isinstance(ids, list) or len(ids) > 100:
                raise ValidationError("Up to 100 products can be saved.")
            for product in s.published().filter(id__in=ids):
                m.Wishlist.objects.get_or_create(user=request.user, product=product)
    return Response(
        {"products": [product_data(p) for p in s.catalog().filter(wishlist__user=request.user)]}
    )


@api_view(["GET", "POST"])
def reviews(request, slug):
    product = get_object_or_404(s.published(), slug=slug)
    if request.method == "GET":
        return Response(
            paginate(
                request,
                product.reviews.filter(status="approved")
                .select_related("user")
                .order_by("-created_at"),
                lambda r: ReviewSerializer(r).data,
            )
        )
    require_user(request)
    csrf(request)
    if not m.OrderItem.objects.filter(
        order__user=request.user, order__status="delivered", variant_size__variant__product=product
    ).exists():
        raise PermissionDenied("Reviews require a delivered purchase.")
    if m.Review.objects.filter(user=request.user, product=product).exists():
        raise ValidationError("You have already reviewed this product.")
    form = ReviewSerializer(data=request.data)
    form.is_valid(raise_exception=True)
    form.save(user=request.user, product=product, status="pending")
    return Response(form.data, status=201)


@api_view(["GET"])
def rewards(request):
    config = s.store_settings()
    entries = (
        m.RewardEntry.objects.filter(user=request.user).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        if request.user.is_authenticated
        else m.RewardEntry.objects.none()
    )
    points = entries.aggregate(total=Sum("points"))["total"] or 0
    return Response(
        {
            "name": config.rewards_name,
            "enabled": config.rewards_enabled,
            "points": points,
            "tier": "Explorer" if points < 1000 else "Insider",
            "ledger": list(
                entries.order_by("-created_at").values("points", "reason", "created_at")[:50]
            ),
            "points_per_100": config.points_per_100,
        }
    )


@api_view(["POST"])
def subscribe(request, kind):
    csrf(request)
    email = serializers.EmailField().run_validation(request.data.get("email"))
    if request.data.get("consent") is not True:
        raise ValidationError("Consent is required.")
    values = {"email": email.lower(), "kind": kind}
    if kind == "restock":
        values["variant_size"] = get_object_or_404(
            m.VariantSize,
            pk=request.data.get("variant_size_id"),
            variant__product__in=s.published(),
        )
    if kind == "release":
        values["release"] = get_object_or_404(
            m.Release, pk=request.data.get("release_id"), active=True
        )
    m.Subscription.objects.get_or_create(**values, active=True)
    return Response(
        {"message": "You are on the list. You can unsubscribe through any notification."},
        status=201,
    )


@api_view(["POST"])
def returns(request):
    require_user(request)
    csrf(request)
    with transaction.atomic():
        order = get_object_or_404(
            m.Order.objects.select_for_update(),
            reference=request.data.get("order_reference"),
            user=request.user,
        )
        delivered = order.history.filter(status="delivered").order_by("-created_at").first()
        if (
            order.status != "delivered"
            or not delivered
            or (timezone.now() - delivered.created_at).days > s.store_settings().return_days
        ):
            raise ValidationError("This order is not currently eligible for a return.")
        items = request.data.get("items", [])
        if not isinstance(items, list) or not items:
            raise ValidationError("Select order items to return.")
        seen = set()
        for item in items:
            line = get_object_or_404(order.items, id=item.get("order_item_id"))
            qty = serializers.IntegerField(min_value=1, max_value=line.quantity).run_validation(
                item.get("quantity")
            )
            if line.id in seen:
                raise ValidationError("Duplicate return item.")
            seen.add(line.id)
            item["quantity"] = qty
        reason = serializers.CharField(max_length=1000).run_validation(request.data.get("reason"))
        record = m.ReturnRequest.objects.create(
            order=order, user=request.user, items=items, reason=reason
        )
        s.transition(order, "return_requested")
    return Response({"id": record.id, "status": record.status}, status=201)


@api_view(["POST"])
def analytics(request):
    csrf(request)
    names = {
        "view_home",
        "view_item_list",
        "view_item",
        "select_color",
        "select_size",
        "add_to_wishlist",
        "add_to_cart",
        "view_cart",
        "begin_checkout",
        "add_shipping_info",
        "add_payment_info",
        "purchase",
        "search",
        "filter",
        "view_release",
    }
    if request.data.get("consent") is not True or request.data.get("name") not in names:
        raise ValidationError("Event is not permitted.")
    product_id = request.data.get("product_id")
    if product_id is not None:
        product_id = serializers.IntegerField(min_value=1).run_validation(product_id)
    m.AnalyticsEvent.objects.create(name=request.data["name"], product_id=product_id)
    return Response(status=204)


@api_view(["GET"])
def policy(request, slug):
    obj = get_object_or_404(m.Policy, slug=slug)
    if not obj.approved and not settings.DEBUG:
        raise Http404
    return Response(
        {
            "title": obj.title,
            "body": obj.body,
            "updated_at": obj.updated_at,
            "approved": obj.approved,
        }
    )
