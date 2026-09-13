from datetime import timedelta
import os
from pathlib import Path
import shutil
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from shop import models as m


def shoe_svg(color, accent, index):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800" viewBox="0 0 1000 800"><defs><linearGradient id="upper" x2="0.2" y2="1"><stop stop-color="{color}"/><stop offset="1" stop-color="{accent}"/></linearGradient><filter id="shadow"><feGaussianBlur stdDeviation="15"/></filter><pattern id="mesh" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#111" opacity=".18"/></pattern></defs><rect width="1000" height="800" fill="{"#eeefeb" if index % 2 else "#f1f0ed"}"/><ellipse cx="510" cy="582" rx="325" ry="24" fill="#172019" opacity=".14" filter="url(#shadow)"/><g transform="rotate(-12 500 410)"><path d="M157 467 Q160 422 231 407 L426 348 Q485 323 559 237 L649 278 L668 347 Q722 373 791 377 L826 466 L786 510 L243 548 L169 520 Z" fill="url(#upper)" stroke="#222" stroke-opacity=".18" stroke-width="3"/><path d="M175 466 L430 366 Q483 343 556 258 L634 296 L654 365 Q730 391 794 393 L808 451 L773 483 L245 524 Z" fill="url(#mesh)"/><path d="M169 478 Q324 493 459 458 Q643 417 823 459 L834 493 Q740 552 551 562 L236 570 Q168 559 156 535 Z" fill="#e5e4db" stroke="#cbcbbf" stroke-width="3"/><path d="M165 531 Q259 555 458 524 L814 488 L803 522 Q679 578 476 582 L231 585 L169 557 Z" fill="{accent}"/><path d="M235 425 Q243 469 298 484 M637 292 L608 428 M700 382 L726 453 M334 392 L370 473" fill="none" stroke="{accent}" stroke-width="23" opacity=".65"/><path d="M429 365 L570 291 M439 383 L583 310 M457 398 L595 328 M476 414 L606 347" fill="none" stroke="#f7f6ed" stroke-width="12" stroke-linecap="round"/><path d="M558 236 Q586 204 623 230 L650 277 L617 296 Z" fill="{accent}"/><path d="M790 373 L804 415 L770 423" fill="none" stroke="{accent}" stroke-width="18" stroke-linecap="round"/><path d="M211 542 L234 566 M263 546 L283 573 M316 541 L334 570 M697 521 L710 543 M749 510 L762 530" stroke="#222" stroke-opacity=".35" stroke-width="5"/></g></svg>'''


class Command(BaseCommand):
    help = "Create clearly marked fictional DEMO catalogue; safe to rerun without overwriting merchant edits."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or os.getenv("USE_S3") == "true":
            raise CommandError("Demo seeding requires DEBUG=true and local media storage.")
        now = timezone.now()
        media = settings.MEDIA_ROOT / "demo"
        media.mkdir(parents=True, exist_ok=True)
        assets = Path(
            os.getenv(
                "DEMO_ASSETS_DIR", str(settings.BASE_DIR.parent / "frontend" / "public" / "images")
            )
        )
        hero = assets / "hero-original.png"
        if hero.exists() and not (media / "hero.png").exists():
            shutil.copy2(hero, media / "hero.png")
        config, _ = m.SiteSettings.objects.get_or_create(pk=1)
        warehouse, _ = m.Location.objects.get_or_create(
            slug="demo-warehouse", defaults={"name": "DEMO Nairobi warehouse"}
        )
        categories = []
        for name in ["Lifestyle", "Running", "Basketball", "Trail", "Slides", "Kids"]:
            category, _ = m.Category.objects.get_or_create(
                slug=name.lower(), defaults={"name": name}
            )
            categories.append(category)
        brands = []
        for name, description in [
            ("ARC", "Everyday design. Unexpected directions."),
            ("VANTA", "Quiet confidence, from court to city."),
            ("RIFT", "Made for the road less followed."),
            ("PACE", "A little further, every day."),
            ("NORTH", "New perspectives on the outdoors."),
            ("FORMA", "Shape your own everyday."),
        ]:
            brand, _ = m.Brand.objects.get_or_create(
                slug=name.lower(),
                defaults={"name": name, "description": description + " Fictional DEMO brand."},
            )
            brands.append(brand)
        sizes = []
        for label in range(36, 46):
            size, _ = m.Size.objects.get_or_create(
                label=str(label), system="EU", defaults={"sort_order": label}
            )
            sizes.append(size)
        products = []
        names = [
            "Velocity 02",
            "Court Theory",
            "Terrain One",
            "Motion Knit",
            "Summit Low",
            "Studio Runner",
            "Flow State",
            "Court 90",
            "Ridge Runner",
            "Tempo Pro",
            "Drift Sandal",
            "Everyday 01",
            "Velocity Junior",
            "Court Mini",
            "Trail Junior",
            "Motion Lite",
            "Summit Air",
            "Studio Slip",
        ]
        palettes = [
            ("Chalk / Moss", "#d9d8c9", "#849072", "green"),
            ("Graphite / Silver", "#53565c", "#979a9e", "black"),
            ("Clay / Sand", "#b87a61", "#d8b9a0", "brown"),
            ("Blue / Cloud", "#a4b8c8", "#536f8b", "blue"),
            ("Oat / Cream", "#dfd6bf", "#aaa28e", "cream"),
            ("Rose / Burgundy", "#c6939e", "#775360", "pink"),
        ]
        for i, name in enumerate(names):
            slug = name.lower().replace(" ", "-")
            product, created = m.Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "brand": brands[i % 6],
                    "category": categories[5 if 12 <= i <= 14 else i % 5],
                    "subtitle": (
                        "Kids’"
                        if 12 <= i <= 14
                        else "Unisex"
                        if i % 3 == 0
                        else "Women’s"
                        if i % 3 == 1
                        else "Men’s"
                    )
                    + " "
                    + ("running shoes" if i % 2 == 0 else "lifestyle shoes"),
                    "gender": "kids" if 12 <= i <= 14 else ["unisex", "women", "men"][i % 3],
                    "age_group": "kids" if 12 <= i <= 14 else "adult",
                    "base_price": 7900 + i * 450,
                    "compare_at_price": 11900 + i * 450 if i % 4 == 0 else None,
                    "status": "published",
                    "is_new": i < 4,
                    "is_featured": i < 8,
                    "is_best_seller": 4 <= i < 8,
                    "is_limited": i == 9,
                    "sort_order": i,
                    "sport": "running" if i % 2 == 0 else "casual",
                    "style": "performance" if i % 2 == 0 else "lifestyle",
                    "description": f"{name} finds the balance between an easy everyday silhouette and thoughtful detail. A textured upper, cushioned footbed and flexible outsole bring a considered finish. Fictional DEMO merchandise; specifications are illustrative, not verified product claims.",
                    "details": [
                        "DEMO textured upper",
                        "DEMO cushioned footbed",
                        "DEMO flexible outsole",
                        "Illustrative product — not offered for real sale",
                    ],
                    "release_at": now + timedelta(days=8) if i == 9 else None,
                },
            )
            products.append(product)
            if not created:
                continue
            for j in range(3 if i % 3 else 5):
                cname, color, accent, family = palettes[(i + j) % 6]
                variant = m.Variant.objects.create(
                    product=product,
                    sku=f"DEMO-{i + 1:02d}-{j + 1}",
                    color_name=cname,
                    color_code=color,
                    color_family=family,
                    is_default=j == 0,
                    sort_order=j,
                    price=product.base_price + j * 300,
                )
                filename = f"shoe-{i}-{j}.svg"
                (media / filename).write_text(shoe_svg(color, accent, i), encoding="utf8")
                # Trusted code-generated SVG; user uploads use ImageField raster validation.
                m.ProductImage.objects.create(
                    variant=variant,
                    image=f"demo/{filename}",
                    alt=f"DEMO {name}, {cname}, lateral view",
                    width=1000,
                    height=800,
                )
                for k, size in enumerate(sizes):
                    sku = m.VariantSize.objects.create(
                        variant=variant, size=size, sku=f"{variant.sku}-EU{size.label}"
                    )
                    m.Inventory.objects.create(
                        variant_size=sku,
                        location=warehouse,
                        on_hand=0
                        if k == 0 or (i == 8 and j == 0)
                        else 1
                        if k == 1
                        else 8 + (i + k) % 9,
                    )
        for name, slug in [
            ("The Daily Rotation", "daily-rotation"),
            ("Built for Movement", "built-for-movement"),
            ("Under KSh 10,000", "under-10000"),
        ]:
            collection, created = m.Collection.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": "An original edit of fictional DEMO footwear.",
                },
            )
            if created:
                collection.products.set(
                    products[:8] if slug == "daily-rotation" else products[6:12]
                )
        m.Announcement.objects.get_or_create(
            text="Your next move starts here. Explore the new rotation.",
            defaults={"href": "/shop?new=true"},
        )
        nav = [
            ("Men", "/men"),
            ("Women", "/women"),
            ("Kids", "/kids"),
            ("New arrivals", "/shop?new=true"),
            ("Brands", "/brands"),
            ("Releases", "/releases"),
            ("Sale", "/sale"),
        ]
        for i, (label, href) in enumerate(nav):
            entry, created = m.Navigation.objects.get_or_create(
                label=label, parent=None, defaults={"href": href, "sort_order": i}
            )
            if created and label in ["Men", "Women", "Kids"]:
                for j, c in enumerate(categories[:5]):
                    m.Navigation.objects.create(
                        label=c.name,
                        href=f"/shop?gender={label.lower()}&category={c.slug}",
                        parent=entry,
                        sort_order=j,
                    )
        blocks = [
            (
                "HERO",
                "MOVE YOUR\nOWN WAY.",
                "New season. New perspective.",
                "Discover a fresh rotation of everyday icons and future favorites.",
                "/shop?new=true",
                "Explore the new arrivals",
                {
                    "eyebrow": "THE NEXT ROTATION / VOL. 01",
                    "image_alt": "Original demonstration sneaker in chalk and lime, suspended in a sunlit studio",
                    "footnote": "01 / THE EVERYDAY, REIMAGINED",
                    "edition": "EST. 2026",
                    "caption": "NEW PERSPECTIVES. SAME FORWARD ENERGY.",
                },
            ),
            (
                "PRODUCT_CAROUSEL",
                "A fresh perspective.",
                "Just landed. Ready for whatever comes next.",
                "",
                "/shop?new=true",
                "Shop new arrivals",
                {},
            ),
            (
                "CATEGORY_GRID",
                "Every move, covered.",
                "Find the pair that fits your world.",
                "",
                "/shop",
                "Shop all",
                {},
            ),
            (
                "EDITORIAL_SPLIT",
                "LESS ROUTINE.\nMORE ROTATION.",
                "The everyday edit",
                "Thoughtful shapes. Unexpected color. Make room for your next everyday favorite.",
                "/collections/daily-rotation",
                "Discover the edit",
                {},
            ),
            (
                "PRODUCT_CAROUSEL",
                "Good company.",
                "The pairs finding their way into every rotation.",
                "",
                "/shop?best=true",
                "Shop bestsellers",
                {},
            ),
            (
                "BRAND_GRID",
                "Different names. Shared energy.",
                "Explore our fictional demonstration brands.",
                "",
                "/brands",
                "All brands",
                {},
            ),
            (
                "NEWSLETTER",
                "Stay one step ahead.",
                "New rotations, upcoming drops, and stories worth opening.",
                "",
                "",
                "Join the list",
                {},
            ),
        ]
        for i, (kind, title, subtitle, body, href, cta, options) in enumerate(blocks):
            if kind == "CATEGORY_GRID":
                options = {
                    "eyebrow": "WHATEVER YOUR DIRECTION",
                    "tiles": [
                        {"title": "Men", "subtitle": "A new everyday.", "href": "/men"},
                        {"title": "Women", "subtitle": "Go your own way.", "href": "/women"},
                        {"title": "Kids", "subtitle": "Big moves. Small feet.", "href": "/kids"},
                    ],
                }
            elif kind == "EDITORIAL_SPLIT":
                options = {
                    "image_alt": "Original SOLELINE demonstration sneaker editorial",
                    "caption": "THE DAILY ROTATION — AN ORIGINAL EDIT",
                }
            elif kind == "PRODUCT_CAROUSEL":
                options = {
                    "eyebrow": "THE COMMUNITY ROTATION"
                    if title == "Good company."
                    else "THE LATEST LINEUP"
                }
            block, created = m.PageSection.objects.get_or_create(
                type=kind,
                title=title,
                defaults={
                    "subtitle": subtitle,
                    "body": body,
                    "href": href,
                    "cta": cta,
                    "settings": options,
                    "sort_order": i,
                    "image": "demo/hero.png" if kind in ["HERO", "EDITORIAL_SPLIT"] else "",
                },
            )
            if created and kind == "PRODUCT_CAROUSEL":
                block.products.set(products[:4] if i == 1 else products[4:8])
            if not created and config.demo and isinstance(block.settings, dict):
                merged = {**options, **block.settings}
                if merged != block.settings:
                    block.settings = merged
                    block.full_clean()
                    block.save(update_fields=["settings"])
        for i, p in enumerate(products[8:12]):
            m.Release.objects.get_or_create(
                slug=p.slug,
                defaults={
                    "name": p.name,
                    "product": p,
                    "release_at": now + timedelta(days=(i + 1) * 3),
                    "description": "A fictional DEMO release. Join the notification list for this demonstration.",
                    "image": p.variants.first().images.first().image.name,
                },
            )
        m.Promotion.objects.get_or_create(
            code="DEMO10",
            defaults={
                "name": "DEMO welcome offer",
                "kind": "percent",
                "value": 10,
                "minimum": 5000,
                "usage_limit": 1000,
                "per_user_limit": 1,
            },
        )
        for slug, title, body in [
            (
                "shipping",
                "Delivery",
                "DEMO policy draft. Standard shipping is calculated in your bag. Kenya delivery only is configured. Actual delivery promises must be approved by the business before launch.",
            ),
            (
                "returns",
                "Returns & exchanges",
                "DEMO policy draft. The demonstration return window is 30 days after delivery. Request a return from your account. Eligibility and refunds require review. Replace with business-approved terms before launch.",
            ),
            (
                "privacy",
                "Privacy & cookies",
                "DEMO policy draft. Essential cookies maintain your session and bag. Optional analytics and recently viewed storage require your consent. No advertising fingerprint is collected. Configure a privacy contact and approved retention policy before launch.",
            ),
            (
                "terms",
                "Terms of use",
                "DEMO storefront. Products and brands are fictional. Test payments do not move money. This draft requires business and legal approval before public commerce.",
            ),
            (
                "help",
                "Help & contact",
                "This is a demonstration storefront. Browse products, save a wishlist and use the explicitly labeled development checkout. A real support email and operating hours must be configured before launch.",
            ),
        ]:
            m.Policy.objects.get_or_create(slug=slug, defaults={"title": title, "body": body})
        call_command("setup_roles")
        self.stdout.write(
            self.style.SUCCESS(
                f"DEMO seed ready: {m.Product.objects.count()} products, {m.Variant.objects.count()} colorways, {m.VariantSize.objects.count()} size SKUs. No customer reviews or admin credentials fabricated."
            )
        )
