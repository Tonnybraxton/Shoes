import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from shop import models as m
from shop import services as s

pytestmark = pytest.mark.django_db


def test_public_catalog_excludes_drafts(client, stock):
    p = stock.variant_size.variant.product
    assert client.get("/api/v1/products/").data["count"] == 1
    p.status = "draft"
    p.save()
    assert client.get("/api/v1/products/").data["count"] == 0
    assert client.get(f"/api/v1/products/{p.slug}/").status_code == 404


def test_product_projection_has_color_prices_and_stock(client, stock):
    data = client.get("/api/v1/products/test-runner/").data
    assert data["variants"][0]["price"] == "10000.00"
    assert data["variants"][0]["sizes"][0]["available"] == 5
    assert data["rating"] is None and data["review_count"] == 0


@pytest.mark.parametrize(
    "query", ["min_price=NaN", "max_price=Infinity", "rating=-1", "page=bad", "ids=bad"]
)
def test_invalid_filters_are_structured_400(client, stock, query):
    result = client.get("/api/v1/products/?" + query)
    assert result.status_code == 400
    assert "error" in result.data


def test_filters_combine(client, stock):
    assert client.get("/api/v1/products/?brand=test-brand&size=42&in_stock=true").data["count"] == 1
    assert client.get("/api/v1/products/?brand=test-brand&size=43").data["count"] == 0


def test_search_sku_and_brand(client, stock):
    assert len(client.get("/api/v1/search/?q=TEST-BLACK").data["products"]) == 1
    assert len(client.get("/api/v1/search/?q=Test%20Brand").data["products"]) == 1


def test_anonymous_csrf_required(stock):
    client = APIClient(enforce_csrf_checks=True)
    denied = client.post(
        "/api/v1/cart/items/",
        {"variant_size_id": stock.variant_size_id, "quantity": 1},
        format="json",
    )
    assert denied.status_code == 403
    token = client.get("/api/v1/session/").data["csrf_token"]
    accepted = client.post(
        "/api/v1/cart/items/",
        {"variant_size_id": stock.variant_size_id, "quantity": 1},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert accepted.status_code == 200


def test_cart_does_not_trust_browser_price(client, stock):
    result = client.post(
        "/api/v1/cart/items/",
        {"variant_size_id": stock.variant_size_id, "quantity": 1, "unit_price": "0.01"},
        format="json",
    )
    assert result.data["subtotal"] == "10000.00"


@pytest.mark.parametrize("quantity", [0, -1, 11, "oops"])
def test_cart_rejects_invalid_quantity(client, stock, quantity):
    assert (
        client.post(
            "/api/v1/cart/items/",
            {"variant_size_id": stock.variant_size_id, "quantity": quantity},
            format="json",
        ).status_code
        == 400
    )


def test_unavailable_size_server_rejected(client, stock):
    stock.on_hand = 0
    stock.save()
    assert (
        client.post(
            "/api/v1/cart/items/",
            {"variant_size_id": stock.variant_size_id, "quantity": 1},
            format="json",
        ).status_code
        == 400
    )


def test_other_guest_cannot_edit_cart(stock):
    owner = APIClient()
    other = APIClient()
    result = owner.post(
        "/api/v1/cart/items/",
        {"variant_size_id": stock.variant_size_id, "quantity": 1},
        format="json",
    )
    item = result.data["items"][0]["id"]
    assert other.delete(f"/api/v1/cart/items/{item}/").status_code == 404


def test_guest_order_requires_signed_token(client, bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    order = s.create_checkout(bag, checkout_data, "guest")
    assert client.get(f"/api/v1/orders/{order.reference}/").status_code == 404
    assert client.get(f"/api/v1/orders/{order.reference}/?token=forged").status_code == 404
    assert (
        client.get(f"/api/v1/orders/{order.reference}/?token={s.tracking_token(order)}").status_code
        == 200
    )


def test_another_user_cannot_read_order(client, bag, checkout_data, settings):
    settings.TEST_PAYMENTS = True
    owner = get_user_model().objects.create_user("owner", password="unique-password-for-owner")
    other = get_user_model().objects.create_user("other", password="unique-password-for-other")
    bag.user = owner
    bag.save()
    order = s.create_checkout(bag, checkout_data, "private")
    client.force_authenticate(other)
    assert client.get(f"/api/v1/orders/{order.reference}/").status_code == 404


def test_wishlist_merges_without_duplicates(client, stock):
    user = get_user_model().objects.create_user("wish", password="a-long-password")
    client.force_authenticate(user)
    product = stock.variant_size.variant.product
    for _ in range(2):
        assert (
            client.post(
                "/api/v1/wishlist/merge/", {"product_ids": [product.id, product.id]}, format="json"
            ).status_code
            == 200
        )
    assert m.Wishlist.objects.count() == 1


def test_review_requires_delivered_purchase(client, stock):
    user = get_user_model().objects.create_user("reviewer", password="a-long-password")
    client.force_authenticate(user)
    assert (
        client.post(
            "/api/v1/products/test-runner/reviews/",
            {"rating": 5, "title": "Fake", "body": "No purchase"},
            format="json",
        ).status_code
        == 403
    )
    assert m.Review.objects.count() == 0


def test_analytics_requires_explicit_consent_and_strips_payload(client):
    assert (
        client.post("/api/v1/analytics/", {"name": "view_home"}, format="json").status_code == 400
    )
    result = client.post(
        "/api/v1/analytics/",
        {"name": "view_home", "consent": True, "email": "never-store@example.test"},
        format="json",
    )
    assert result.status_code == 204
    assert not hasattr(m.AnalyticsEvent.objects.get(), "email")


def test_address_ownership(client):
    User = get_user_model()
    one = User.objects.create_user("one")
    two = User.objects.create_user("two")
    address = m.Address.objects.create(user=one, line1="Street", city="Nairobi", county="Nairobi")
    client.force_authenticate(two)
    assert client.delete(f"/api/v1/addresses/{address.id}/").status_code == 404


def test_subscription_requires_consent(client):
    assert (
        client.post(
            "/api/v1/newsletter/", {"email": "person@example.test", "consent": False}, format="json"
        ).status_code
        == 400
    )
    assert not m.Subscription.objects.exists()


def test_payment_simulation_hidden_when_disabled(client, settings):
    settings.TEST_PAYMENTS = False
    assert client.post("/api/v1/payments/test/complete/", {}, format="json").status_code == 404


def test_invalid_stripe_signature_rejected(client, settings):
    settings.STRIPE_WEBHOOK_SECRET = "test-signature-secret"
    assert (
        client.post(
            "/api/v1/payments/stripe/webhook/", {}, format="json", HTTP_STRIPE_SIGNATURE="fake"
        ).status_code
        == 400
    )


def test_admin_requires_staff(client):
    assert client.get("/admin/").status_code == 302
