import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from shop.models import Inventory, VariantSize, Location


class Command(BaseCommand):
    help = "Validate inventory CSV (sku,location,on_hand). Dry-run by default; --apply writes atomically."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        rows = []
        seen = set()
        with Path(options["path"]).open(encoding="utf-8-sig", newline="") as stream:
            for line, row in enumerate(csv.DictReader(stream), 2):
                try:
                    sku = VariantSize.objects.get(sku=row["sku"])
                    location = Location.objects.get(slug=row["location"])
                    quantity = int(row["on_hand"])
                    if quantity < 0 or (sku.pk, location.pk) in seen:
                        raise ValueError("Negative stock or duplicate SKU/location")
                    seen.add((sku.pk, location.pk))
                    rows.append((sku, location, quantity))
                except (
                    KeyError,
                    ValueError,
                    VariantSize.DoesNotExist,
                    Location.DoesNotExist,
                ) as exc:
                    raise CommandError(f"Line {line}: {exc}")
        with transaction.atomic():
            for sku, location, quantity in rows:
                stock, _ = Inventory.objects.select_for_update().get_or_create(
                    variant_size=sku, location=location
                )
                if quantity < stock.reserved:
                    raise CommandError(f"{sku.sku}: stock cannot be below reserved quantity.")
                stock.on_hand = quantity
                stock.full_clean()
                stock.save()
            if not options["apply"]:
                transaction.set_rollback(True)
        self.stdout.write(
            self.style.SUCCESS(
                f"{len(rows)} validated rows. "
                + ("Applied." if options["apply"] else "Dry run; nothing changed.")
            )
        )
