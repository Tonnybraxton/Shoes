from django.utils import timezone
from rest_framework import serializers
from . import models as m
from .services import available, money


def product_data(product):
    now = timezone.now()
    variants = []
    for variant in product.variants.all():
        if not variant.active:
            continue
        images = [
            {
                "id": i.id,
                "url": i.image.url,
                "alt": i.alt,
                "view_type": i.view_type,
                "width": i.width,
                "height": i.height,
                "renditions": i.image_data,
            }
            for i in variant.images.all()
        ]
        sizes = [
            {
                "id": s.id,
                "size_id": s.size_id,
                "label": s.size.label,
                "system": s.size.system,
                "sku": s.sku,
                "available": available(s)
                if (not variant.release_at or variant.release_at <= now)
                and (not product.release_at or product.release_at <= now)
                else 0,
            }
            for s in variant.sizes.all()
        ]
        variants.append(
            {
                "id": variant.id,
                "sku": variant.sku,
                "color_name": variant.color_name,
                "color_code": variant.color_code,
                "color_family": variant.color_family,
                "price": money(variant.effective_price),
                "compare_at_price": money(variant.compare_at_price or product.compare_at_price)
                if variant.compare_at_price or product.compare_at_price
                else None,
                "is_default": variant.is_default,
                "in_stock": any(s["available"] > 0 for s in sizes),
                "image": images[0]["url"] if images else "",
                "hover_image": next((i["url"] for i in images if i["view_type"] == "HOVER"), ""),
                "images": images,
                "sizes": sizes,
            }
        )
    badges = [
        b.label
        for b in product.merch_badges.all()
        if (not b.starts_at or b.starts_at <= now) and (not b.ends_at or b.ends_at > now)
    ]
    if not badges:
        badges = (
            ["New arrival"]
            if product.is_new
            else ["Limited release"]
            if product.is_limited
            else ["Bestseller"]
            if product.is_best_seller
            else []
        )
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "subtitle": product.subtitle,
        "description": product.description,
        "brand": {
            "id": product.brand_id,
            "name": product.brand.name,
            "slug": product.brand.slug,
            "logo": product.brand.logo.url if product.brand.logo else "",
        },
        "category": {
            "id": product.category_id,
            "name": product.category.name,
            "slug": product.category.slug,
        },
        "gender": product.gender,
        "age_group": product.age_group,
        "sport": product.sport,
        "style": product.style,
        "price": money(product.base_price),
        "compare_at_price": money(product.compare_at_price) if product.compare_at_price else None,
        "rating": str(product.rating_cached)
        if product.review_count and product.rating_cached
        else None,
        "review_count": product.review_count,
        "is_new": product.is_new,
        "is_featured": product.is_featured,
        "is_best_seller": product.is_best_seller,
        "is_limited": product.is_limited,
        "see_price_in_bag": product.see_price_in_bag,
        "badges": badges,
        "default_variant_id": next(
            (v["id"] for v in variants if v["is_default"]), variants[0]["id"] if variants else None
        ),
        "max_card_swatches": product.max_card_swatches,
        "fit": product.fit,
        "width": product.width,
        "details": product.details,
        "variants": variants,
        "seo_title": product.seo_title,
        "seo_description": product.seo_description,
    }


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Address
        fields = ["id", "label", "line1", "line2", "city", "county", "postal_code", "country"]

    def validate_country(self, value):
        if value != "KE":
            raise serializers.ValidationError("Only Kenya shipping is currently configured.")
        return value


class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.RegexField(r"^\+?[0-9 ()-]{7,25}$")
    address = AddressSerializer()
    shipping_method = serializers.ChoiceField(choices=["standard"])
    payment_provider = serializers.ChoiceField(choices=["stripe", "test"])
    consent = serializers.BooleanField()

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("Agreement to checkout terms is required.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    verified_purchase = serializers.SerializerMethodField()

    class Meta:
        model = m.Review
        fields = [
            "id",
            "rating",
            "title",
            "body",
            "fit",
            "comfort",
            "created_at",
            "author",
            "verified_purchase",
            "status",
        ]
        read_only_fields = ["status"]

    def get_author(self, obj):
        return obj.user.first_name or "Customer"

    def get_verified_purchase(self, obj):
        return True


def order_data(order):
    return {
        "reference": str(order.reference),
        "status": order.status,
        "email": order.email,
        "created_at": order.created_at,
        "items": list(
            order.items.values(
                "id",
                "product_name",
                "product_slug",
                "brand",
                "color_name",
                "size_label",
                "image",
                "quantity",
                "unit_price",
                "line_total",
            )
        ),
        "subtotal": money(order.subtotal),
        "discount": money(order.discount),
        "shipping": money(order.shipping),
        "total": money(order.total),
        "currency": order.currency,
        "address": order.address,
        "history": list(
            order.history.order_by("created_at").values("status", "note", "created_at")
        ),
    }
