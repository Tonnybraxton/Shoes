import pytest
from rest_framework.test import APIClient
from shop import models as m


@pytest.fixture
def stock(db):
    brand = m.Brand.objects.create(name="Test Brand", slug="test-brand")
    category = m.Category.objects.create(name="Running", slug="running")
    product = m.Product.objects.create(
        name="Test Runner",
        slug="test-runner",
        brand=brand,
        category=category,
        status="published",
        base_price="10000.00",
    )
    variant = m.Variant.objects.create(
        product=product, sku="TEST-BLACK", color_name="Black", color_family="black", is_default=True
    )
    size = m.Size.objects.create(label="42", system="EU", sort_order=42)
    sku = m.VariantSize.objects.create(variant=variant, size=size, sku="TEST-BLACK-42")
    location = m.Location.objects.create(name="Warehouse", slug="warehouse")
    inventory = m.Inventory.objects.create(variant_size=sku, location=location, on_hand=5)
    return inventory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def checkout_data():
    return {
        "email": "buyer@example.test",
        "first_name": "Test",
        "last_name": "Buyer",
        "phone": "+254700000000",
        "address": {
            "line1": "1 Test Lane",
            "line2": "",
            "city": "Nairobi",
            "county": "Nairobi",
            "postal_code": "00100",
            "country": "KE",
        },
        "shipping_method": "standard",
        "payment_provider": "test",
        "consent": True,
    }


@pytest.fixture
def bag(stock):
    cart = m.Cart.objects.create()
    m.CartItem.objects.create(cart=cart, variant_size=stock.variant_size, quantity=1)
    return cart
