import csv
from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.utils.html import format_html
from . import models as m
from .services import transition


class AuditedAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        m.AuditLog.objects.create(
            actor=request.user,
            action="change" if change else "create",
            object_type=obj._meta.label,
            object_id=str(obj.pk),
            detail={"fields": form.changed_data},
        )


class VariantInline(admin.TabularInline):
    model = m.Variant
    extra = 0
    show_change_link = True
    fields = [
        "sku",
        "color_name",
        "color_code",
        "color_family",
        "price",
        "is_default",
        "active",
        "sort_order",
    ]


class BadgeInline(admin.TabularInline):
    model = m.Badge
    extra = 0


class ImageInline(admin.TabularInline):
    model = m.ProductImage
    extra = 0
    readonly_fields = ["preview", "width", "height"]
    fields = ["preview", "image", "alt", "view_type", "sort_order", "width", "height"]

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.pk or not obj.image:
            return "Upload an image"
        return format_html(
            '<img src="{}" alt="{}" width="120" style="height:auto" />', obj.image.url, obj.alt
        )


class SizeInline(admin.TabularInline):
    model = m.VariantSize
    extra = 0
    autocomplete_fields = ["size"]
    show_change_link = True


class InventoryForm(forms.ModelForm):
    class Meta:
        model = m.Inventory
        fields = "__all__"

    def clean(self):
        data = super().clean()
        if self.instance.pk:
            current = m.Inventory.objects.select_for_update().get(pk=self.instance.pk)
            self.instance.reserved = current.reserved
            for key in ("variant_size", "location"):
                if key in data and data[key].pk != getattr(current, f"{key}_id"):
                    self.add_error(
                        key, "Create a separate stock record to change the SKU or location."
                    )
            if data.get("on_hand", current.on_hand) < current.reserved:
                self.add_error("on_hand", "Stock cannot fall below currently reserved units.")
        return data


class InventoryInline(admin.TabularInline):
    model = m.Inventory
    extra = 0
    form = InventoryForm
    readonly_fields = ["reserved"]


@admin.register(m.Product)
class ProductAdmin(AuditedAdmin):
    list_display = [
        "name",
        "brand",
        "gender",
        "status",
        "base_price",
        "is_featured",
        "is_new",
        "sort_order",
        "updated_at",
    ]
    list_filter = [
        "status",
        "brand",
        "category",
        "gender",
        "is_featured",
        "is_new",
        "is_best_seller",
    ]
    search_fields = ["name", "slug", "model_family", "variants__sku"]
    prepopulated_fields = {"slug": ["name"]}
    autocomplete_fields = ["brand", "category", "collections"]
    list_select_related = ["brand", "category"]
    list_editable = ["status", "is_featured", "sort_order"]
    inlines = [VariantInline, BadgeInline]
    actions = ["publish", "feature", "export_csv"]

    @admin.action(description="Publish selected products")
    def publish(self, request, qs):
        for p in qs:
            p.status = "published"
            p.save()

    @admin.action(description="Feature selected products")
    def feature(self, request, qs):
        for p in qs:
            p.is_featured = True
            p.save()

    @admin.action(description="Export selected catalogue to CSV")
    def export_csv(self, request, qs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="catalog.csv"'
        writer = csv.writer(response)
        writer.writerow(["slug", "name", "brand", "base_price", "status"])
        for p in qs.select_related("brand"):
            writer.writerow(
                [
                    csv_cell(value)
                    for value in [p.slug, p.name, p.brand.slug, p.base_price, p.status]
                ]
            )
        return response


@admin.register(m.Variant)
class VariantAdmin(AuditedAdmin):
    list_display = ["sku", "product", "color_name", "price", "is_default", "active", "sort_order"]
    list_filter = ["active", "color_family", "is_default"]
    search_fields = ["sku", "product__name", "color_name"]
    autocomplete_fields = ["product"]
    list_select_related = ["product"]
    inlines = [ImageInline, SizeInline]


@admin.register(m.VariantSize)
class VariantSizeAdmin(AuditedAdmin):
    list_display = ["sku", "variant", "size"]
    search_fields = ["sku", "variant__product__name"]
    autocomplete_fields = ["variant", "size"]
    list_select_related = ["variant__product", "size"]
    inlines = [InventoryInline]


@admin.register(m.Inventory)
class InventoryAdmin(AuditedAdmin):
    form = InventoryForm
    list_display = [
        "variant_size",
        "location",
        "on_hand",
        "reserved",
        "available",
        "low_stock_threshold",
    ]
    search_fields = ["variant_size__sku"]
    list_filter = ["location"]
    readonly_fields = ["reserved"]
    autocomplete_fields = ["variant_size"]
    list_select_related = ["variant_size", "location"]


class ImmutableInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderItemInline(ImmutableInline):
    model = m.OrderItem


class HistoryInline(ImmutableInline):
    model = m.OrderHistory


@admin.register(m.Order)
class OrderAdmin(AuditedAdmin):
    list_display = [
        "reference",
        "email",
        "status",
        "total",
        "currency",
        "payment_provider",
        "created_at",
    ]
    list_filter = ["status", "payment_provider", "created_at"]
    search_fields = ["reference", "email"]
    readonly_fields = [f.name for f in m.Order._meta.fields]
    inlines = [OrderItemInline, HistoryInline]
    actions = ["processing", "packed", "shipped", "delivered"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def move(self, request, qs, target):
        for candidate in qs:
            try:
                with transaction.atomic():
                    order = m.Order.objects.select_for_update().get(pk=candidate.pk)
                    transition(order, target, "Admin fulfillment update")
                    m.AuditLog.objects.create(
                        actor=request.user,
                        action="transition",
                        object_type="Order",
                        object_id=str(order.reference),
                        detail={"target": target},
                    )
            except Exception as exc:
                self.message_user(request, f"{candidate.reference}: {exc}", messages.ERROR)

    @admin.action(description="Start processing")
    def processing(self, request, qs):
        self.move(request, qs, "processing")

    @admin.action(description="Mark packed")
    def packed(self, request, qs):
        self.move(request, qs, "packed")

    @admin.action(description="Mark shipped")
    def shipped(self, request, qs):
        self.move(request, qs, "shipped")

    @admin.action(description="Mark delivered")
    def delivered(self, request, qs):
        self.move(request, qs, "delivered")


@admin.register(m.Review)
class ReviewAdmin(AuditedAdmin):
    list_display = ["product", "user", "rating", "status", "created_at"]
    list_filter = ["status", "rating"]
    search_fields = ["product__name", "title"]
    actions = ["approve", "reject"]

    def moderate(self, request, qs, status):
        ids = set(qs.values_list("product_id", flat=True))
        qs.update(status=status)
        for pk in ids:
            result = m.Review.objects.filter(product_id=pk, status="approved").aggregate(
                rating=Avg("rating"), count=Count("id")
            )
            m.Product.objects.filter(pk=pk).update(
                rating_cached=result["rating"], review_count=result["count"]
            )

    @admin.action(description="Approve verified reviews")
    def approve(self, request, qs):
        self.moderate(request, qs, "approved")

    @admin.action(description="Reject reviews")
    def reject(self, request, qs):
        self.moderate(request, qs, "rejected")


class NamedAdmin(AuditedAdmin):
    list_display = ["name", "slug", "active", "sort_order"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    list_editable = ["active", "sort_order"]


for model in [m.Brand, m.Category, m.Collection, m.Location]:
    admin.site.register(model, NamedAdmin)


@admin.register(m.Size)
class SizeAdmin(AuditedAdmin):
    search_fields = ["label", "system"]
    list_display = ["label", "system", "sort_order"]


@admin.register(m.PageSection)
class PageSectionAdmin(AuditedAdmin):
    list_display = ["title", "type", "active", "sort_order", "starts_at", "ends_at"]
    list_editable = ["active", "sort_order"]
    list_filter = ["type", "active"]
    autocomplete_fields = ["products"]


def csv_cell(value):
    value = str(value)
    return (
        "'" + value
        if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n"))
        else value
    )


@admin.register(m.Release)
class ReleaseAdmin(NamedAdmin):
    list_display = ["name", "release_at", "product", "active", "sold_out"]
    list_editable = ["active"]
    autocomplete_fields = ["product"]


class LedgerAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


for model in [m.PaymentEvent, m.RewardEntry, m.AuditLog, m.Reservation, m.AnalyticsEvent]:
    admin.site.register(model, LedgerAdmin)
for model in [
    m.SiteSettings,
    m.Announcement,
    m.Navigation,
    m.Policy,
    m.Profile,
    m.Address,
    m.Promotion,
    m.Subscription,
    m.ReturnRequest,
    m.Outbox,
]:
    admin.site.register(model, AuditedAdmin)
