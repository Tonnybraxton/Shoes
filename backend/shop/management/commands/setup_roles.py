from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLE_MODELS = {
    "Content editor": ["pagesection", "announcement", "navigation", "policy"],
    "Merchandiser": [
        "product",
        "variant",
        "productimage",
        "brand",
        "category",
        "collection",
        "badge",
        "release",
    ],
    "Inventory manager": ["inventory", "variantsize", "size", "location"],
    "Order manager": ["order", "returnrequest"],
    "Support": ["order", "returnrequest", "profile"],
    "Marketing": ["promotion", "subscription", "release", "pagesection"],
}


class Command(BaseCommand):
    help = "Create staff role groups without creating users or changing existing group permissions."

    def handle(self, *args, **options):
        created_count = 0
        for name, models in ROLE_MODELS.items():
            group, created = Group.objects.get_or_create(name=name)
            if created:
                permissions = Permission.objects.filter(
                    content_type__app_label="shop", content_type__model__in=models
                ).exclude(codename__startswith="delete_")
                if name == "Support":
                    permissions = permissions.filter(codename__startswith="view_")
                group.permissions.set(permissions)
                created_count += 1
        self.stdout.write(
            f"Created {created_count} role groups; existing permissions preserved. No users created."
        )
