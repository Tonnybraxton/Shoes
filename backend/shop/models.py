import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from django.core.exceptions import ValidationError
from .media import ProcessedImageField
from .content import validate_section_settings, validate_local_href


class Named(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = ProcessedImageField(upload_to="editorial/", blank=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Brand(Named):
    logo = ProcessedImageField(upload_to="brands/", blank=True)


class Category(Named):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    gender = models.CharField(max_length=20, blank=True)


class Collection(Named):
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional filters: gender, brand, category, is_new, is_best_seller.",
    )


class Product(Named):
    STATUS = [("draft", "Draft"), ("published", "Published"), ("archived", "Archived")]
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    collections = models.ManyToManyField(Collection, blank=True, related_name="products")
    model_family = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=160, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[("men", "Men"), ("women", "Women"), ("kids", "Kids"), ("unisex", "Unisex")],
        default="unisex",
        db_index=True,
    )
    age_group = models.CharField(max_length=20, default="adult", db_index=True)
    sport = models.CharField(max_length=50, blank=True, db_index=True)
    style = models.CharField(max_length=50, blank=True, db_index=True)
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="draft", db_index=True)
    release_at = models.DateTimeField(null=True, blank=True)
    visible_from = models.DateTimeField(null=True, blank=True)
    visible_until = models.DateTimeField(null=True, blank=True)
    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_limited = models.BooleanField(default=False)
    is_exclusive = models.BooleanField(default=False)
    promo_eligible = models.BooleanField(default=True)
    free_shipping = models.BooleanField(default=False)
    see_price_in_bag = models.BooleanField(default=False)
    max_card_swatches = models.PositiveSmallIntegerField(
        default=4, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    fit = models.CharField(
        max_length=12,
        choices=[("small", "Runs small"), ("true", "True to size"), ("large", "Runs large")],
        default="true",
    )
    width = models.CharField(max_length=20, default="regular")
    details = models.JSONField(default=list, blank=True)
    rating_cached = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(Named.Meta):
        constraints = [
            models.CheckConstraint(condition=Q(base_price__gte=0), name="product_price_nonnegative")
        ]
        indexes = [
            models.Index(fields=["status", "gender", "sort_order"]),
            models.Index(fields=["brand", "status"]),
        ]


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=80, unique=True)
    color_name = models.CharField(max_length=80)
    color_code = models.CharField(
        max_length=7, default="#dddddd", validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$")]
    )
    color_family = models.CharField(max_length=30, db_index=True)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=60, blank=True)
    release_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"], condition=Q(is_default=True), name="one_default_variant"
            ),
            models.CheckConstraint(
                condition=Q(price__isnull=True) | Q(price__gte=0), name="variant_price_nonnegative"
            ),
        ]

    def __str__(self):
        return f"{self.product.name} / {self.color_name}"

    @property
    def effective_price(self):
        return self.price if self.price is not None else self.product.base_price


class ProductImage(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="images")
    image = ProcessedImageField(
        upload_to="products/%Y/%m/", width_field="width", height_field="height"
    )
    original = models.FileField(upload_to="originals/%Y/%m/", blank=True, editable=False)
    renditions = models.JSONField(default=dict, blank=True, editable=False)
    alt = models.CharField(max_length=220)
    view_type = models.CharField(
        max_length=20,
        choices=[
            (v, v.title())
            for v in [
                "PRIMARY",
                "LATERAL",
                "MEDIAL",
                "TOP",
                "REAR",
                "SOLE",
                "DETAIL",
                "LIFESTYLE",
                "HOVER",
                "360_FRAME",
            ]
        ],
        default="PRIMARY",
    )
    sort_order = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=1000)
    height = models.PositiveIntegerField(default=800)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.alt

    @property
    def image_data(self):
        return [
            {
                "url": self.image.storage.url(item["name"]),
                "width": int(width),
                "height": item["height"],
            }
            for width, item in sorted(self.renditions.items(), key=lambda pair: int(pair[0]))
        ]


class Size(models.Model):
    label = models.CharField(max_length=20)
    system = models.CharField(
        max_length=20,
        choices=[(v, v) for v in ["EU", "UK", "US Men", "US Women", "US Kids"]],
        default="EU",
    )
    sort_order = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        ordering = ["system", "sort_order"]
        constraints = [
            models.UniqueConstraint(fields=["label", "system"], name="unique_size_system")
        ]

    def __str__(self):
        return f"{self.system} {self.label}"


class VariantSize(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="sizes")
    size = models.ForeignKey(Size, on_delete=models.PROTECT)
    sku = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["size__sort_order"]
        constraints = [
            models.UniqueConstraint(fields=["variant", "size"], name="unique_variant_size")
        ]

    def __str__(self):
        return self.sku


class Location(Named):
    is_store = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    hours = models.JSONField(default=dict, blank=True)
    pickup_enabled = models.BooleanField(default=False)


class Inventory(models.Model):
    variant_size = models.ForeignKey(
        VariantSize, on_delete=models.CASCADE, related_name="inventory"
    )
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant_size", "location"], name="unique_stock_location"
            ),
            models.CheckConstraint(
                condition=Q(on_hand__gte=F("reserved")), name="stock_covers_reservations"
            ),
        ]

    @property
    def available(self):
        return self.on_hand - self.reserved

    def __str__(self):
        return f"{self.variant_size.sku}: {self.available}"


class Badge(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="merch_badges")
    label = models.CharField(max_length=40)
    priority = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["priority"]


class SiteSettings(models.Model):
    name = models.CharField(max_length=80, default="SOLELINE")
    tagline = models.CharField(max_length=160, default="Find your next move.")
    demo = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=15000)
    standard_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=350)
    return_days = models.PositiveIntegerField(default=30)
    rewards_name = models.CharField(max_length=80, default="SOLELINE Circle")
    points_per_100 = models.PositiveIntegerField(default=1)
    rewards_enabled = models.BooleanField(default=True)

    # Optional workflows remain disabled in API until fully implemented.
    def __str__(self):
        return self.name


class Scheduled(models.Model):
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]

    def clean(self):
        super().clean()
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must follow start time."})


class Announcement(Scheduled):
    text = models.CharField(max_length=200)
    href = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=2, blank=True)
    campaign = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.text


class Navigation(Scheduled):
    label = models.CharField(max_length=80)
    href = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    def __str__(self):
        return self.label


class PageSection(Scheduled):
    type = models.CharField(
        max_length=30,
        choices=[
            (v, v.replace("_", " ").title())
            for v in [
                "HERO",
                "PRODUCT_CAROUSEL",
                "CATEGORY_GRID",
                "BRAND_GRID",
                "EDITORIAL_SPLIT",
                "VIDEO",
                "DROP_COUNTDOWN",
                "PROMO_BANNER",
                "REWARDS",
                "TRUST_BAR",
                "RICH_TEXT",
                "NEWSLETTER",
            ]
        ],
    )
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    image = ProcessedImageField(upload_to="editorial/", blank=True)
    href = models.CharField(max_length=200, blank=True)
    cta = models.CharField(max_length=80, blank=True)
    settings = models.JSONField(
        default=dict, blank=True, help_text="Structured settings, never arbitrary HTML."
    )
    products = models.ManyToManyField(Product, blank=True)

    def clean(self):
        super().clean()
        validate_section_settings(self.settings)
        if self.href:
            validate_local_href(self.href)

    def __str__(self):
        return f"{self.type}: {self.title}"


class Policy(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    body = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=30, blank=True)
    usual_size = models.CharField(max_length=20, blank=True)
    size_system = models.CharField(max_length=20, default="EU")
    fit_preference = models.CharField(max_length=20, default="regular")
    email_verified = models.BooleanField(default=False)


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    label = models.CharField(max_length=50, default="Home")
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default="KE")


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="one_wishlist_product")
        ]


class Promotion(Scheduled):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    kind = models.CharField(
        max_length=20,
        choices=[("percent", "Percent"), ("fixed", "Fixed amount"), ("shipping", "Free shipping")],
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    minimum = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(default=1000)
    per_user_limit = models.PositiveIntegerField(default=1)
    uses = models.PositiveIntegerField(default=0)
    members_only = models.BooleanField(default=False)
    automatic = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True)
    brands = models.ManyToManyField(Brand, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.code


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    promo_code = models.CharField(max_length=40, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant_size = models.ForeignKey(VariantSize, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant_size"], name="unique_cart_size"),
            models.CheckConstraint(
                condition=Q(quantity__gte=1) & Q(quantity__lte=10), name="cart_quantity_range"
            ),
        ]


class Order(models.Model):
    STATES = [
        "pending",
        "payment_pending",
        "paid",
        "processing",
        "packed",
        "shipped",
        "ready_pickup",
        "delivered",
        "cancelled",
        "refund_pending",
        "refunded",
        "return_requested",
        "returned",
    ]
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=100)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20,
        choices=[(v, v.replace("_", " ").title()) for v in STATES],
        default="pending",
        db_index=True,
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    address = models.JSONField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    promo_code = models.CharField(max_length=40, blank=True)
    payment_provider = models.CharField(max_length=20)
    payment_session = models.CharField(max_length=250, blank=True)
    payment_url = models.URLField(max_length=1000, blank=True)
    expires_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "idempotency_key"], name="unique_checkout_attempt"
            ),
            models.CheckConstraint(condition=Q(total__gte=0), name="order_total_nonnegative"),
        ]

    def __str__(self):
        return str(self.reference)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant_size = models.ForeignKey(VariantSize, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    product_slug = models.CharField(max_length=160)
    brand = models.CharField(max_length=160)
    color_name = models.CharField(max_length=80)
    size_label = models.CharField(max_length=40)
    sku = models.CharField(max_length=100)
    image = models.CharField(max_length=300, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)


class Reservation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservations")
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    released = models.BooleanField(default=False)


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentEvent(models.Model):
    provider = models.CharField(max_length=20)
    event_id = models.CharField(max_length=200, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class RewardEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    points = models.IntegerField()
    reason = models.CharField(max_length=160)
    dedupe_key = models.CharField(max_length=200, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=2000)
    fit = models.CharField(max_length=20, default="true")
    comfort = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(
        max_length=12,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="one_review_per_buyer")
        ]


class Release(Named):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    release_at = models.DateTimeField(db_index=True)
    sold_out = models.BooleanField(default=False)


class Subscription(models.Model):
    email = models.EmailField()
    kind = models.CharField(
        max_length=20,
        choices=[("newsletter", "Newsletter"), ("restock", "Restock"), ("release", "Release")],
    )
    variant_size = models.ForeignKey(VariantSize, on_delete=models.CASCADE, null=True, blank=True)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, null=True, blank=True)
    consent_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)


class ReturnRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="returns")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    items = models.JSONField()
    reason = models.TextField(max_length=1000)
    request_type = models.CharField(max_length=20, default="refund")
    status = models.CharField(
        max_length=20,
        choices=[
            (v, v.title()) for v in ["requested", "approved", "rejected", "received", "refunded"]
        ],
        default="requested",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Outbox(models.Model):
    kind = models.CharField(max_length=40)
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    dedupe_key = models.CharField(max_length=240, unique=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=120)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=80)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AnalyticsEvent(models.Model):
    name = models.CharField(max_length=40)
    product_id = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
