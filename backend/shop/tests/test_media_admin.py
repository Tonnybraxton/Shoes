from io import BytesIO, StringIO

import pytest
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from shop import models as m
from shop.admin import InventoryForm, csv_cell
from shop.content import validate_section_settings
from shop.media import decode_upload, MAX_UPLOAD_BYTES

pytestmark = pytest.mark.django_db


def upload(width=2400, height=1600):
    stream = BytesIO()
    Image.new("RGB", (width, height), "#667788").save(stream, format="PNG")
    return SimpleUploadedFile("test.png", stream.getvalue(), content_type="image/png")


def test_product_upload_preserves_original_and_encodes_responsive_sizes(stock, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    picture = m.ProductImage.objects.create(
        variant=stock.variant_size.variant, image=upload(), alt="Test shoe"
    )
    picture.refresh_from_db()
    assert picture.image.name.endswith(".webp")
    assert picture.original.name.endswith(".png")
    assert (picture.width, picture.height) == (2000, 1333)
    assert [item["width"] for item in picture.image_data] == [160, 480, 800, 1200, 1600]
    for item in picture.renditions.values():
        with picture.image.storage.open(item["name"]) as data, Image.open(data) as image:
            assert image.format == "WEBP"
            assert image.height == item["height"]
            assert not image.getexif()
    original_name = picture.original.name
    rendition_names = picture.renditions.copy()
    picture.alt = "Updated descriptive alt"
    picture.save()
    assert picture.original.name == original_name
    assert picture.renditions == rendition_names


@pytest.mark.parametrize(
    "payload",
    [b"<svg onload='alert(1)'></svg>", b"not an image", b"x" * (MAX_UPLOAD_BYTES + 1)],
    ids=["svg", "invalid-image", "oversized-upload"],
)
def test_invalid_uploads_rejected_before_writing(stock, settings, tmp_path, payload):
    settings.MEDIA_ROOT = tmp_path
    with pytest.raises(ValidationError):
        m.ProductImage.objects.create(
            variant=stock.variant_size.variant,
            alt="Invalid",
            image=SimpleUploadedFile("fake.png", payload, content_type="image/png"),
        )
    assert not list(tmp_path.rglob("*"))


def test_editorial_upload_processed_and_small_images_not_upscaled(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    brand = m.Brand.objects.create(name="Brand", slug="brand", logo=upload(80, 50))
    with brand.logo.open() as data, Image.open(data) as image:
        assert image.size == (80, 50)
        assert image.format == "WEBP"


def test_oversized_dimensions_rejected_before_decode():
    with pytest.raises(ValidationError, match="25 million"):
        decode_upload(upload(5001, 5000))


@pytest.mark.parametrize(
    "settings_value",
    [
        [],
        {"tiles": []},
        {"caption": {}},
        {"tiles": [{"title": "Tile", "subtitle": "", "href": "//attacker.test"}]},
    ],
)
def test_structured_content_rejects_invalid_shape(settings_value):
    with pytest.raises(ValidationError):
        validate_section_settings(settings_value)


def test_inventory_admin_rechecks_reserved_count_and_protects_ledger(stock):
    stale = m.Inventory.objects.get(pk=stock.pk)
    m.Inventory.objects.filter(pk=stock.pk).update(reserved=4)
    with transaction.atomic():
        form = InventoryForm(
            data={
                "variant_size": stock.variant_size_id,
                "location": stock.location_id,
                "on_hand": 3,
                "reserved": 0,
                "low_stock_threshold": 3,
            },
            instance=stale,
        )
        assert not form.is_valid()
        assert "on_hand" in form.errors


def test_setup_roles_preserves_existing_permissions():
    group = Group.objects.create(name="Support")
    permission = Permission.objects.filter(codename="view_product").get()
    group.permissions.add(permission)
    call_command("setup_roles", stdout=StringIO())
    assert list(group.permissions.all()) == [permission]
    assert Group.objects.filter(name="Merchandiser").exists()


def test_admin_csv_cannot_inject_spreadsheet_formulas():
    assert csv_cell("=HYPERLINK(1)").startswith("'")
    assert csv_cell("  +1+1").startswith("'")
    assert csv_cell("Ordinary product") == "Ordinary product"
