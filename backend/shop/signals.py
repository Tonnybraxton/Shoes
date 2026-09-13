from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    Product,
    Variant,
    Inventory,
    ProductImage,
    Announcement,
    Navigation,
    PageSection,
    SiteSettings,
    Brand,
    Category,
    Review,
)


@receiver(post_save)
@receiver(post_delete)
def invalidate_catalog(sender, **kwargs):
    if sender in {
        Product,
        Variant,
        Inventory,
        ProductImage,
        Announcement,
        Navigation,
        PageSection,
        SiteSettings,
        Brand,
        Category,
        Review,
    }:
        cache.delete("catalog:facets")
        # Public projections are currently read-through, uncached for correctness.
