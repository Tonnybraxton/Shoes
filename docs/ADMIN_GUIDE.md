# Admin guide

Use `/admin/` on Django's local port, or on the shared store origin behind nginx. Create a superuser using the README commands. Give ordinary operators `is_staff` plus the relevant role group. Support receives view permissions; existing group customizations survive `setup_roles`.

## Catalogue workflow

1. Add or select a Brand and Category. Their slugs determine directory links. Add Collections for editorial selections.
2. Add a Product with name, slug, brand, category, base price, description, gender and status **Draft**. Configure fit, width, product details, SEO fields and visibility/release times.
3. Save the product. Add colourways in its Variants inline: unique SKU, colour name, CSS hex colour, colour family, optional price override, sort order, active state and default flag. Only one default is allowed per product.
4. Open each Variant's change page. Add image rows with descriptive alt text, view type and order. The first image by sort order is the card image; a HOVER image supplies the alternate card image.
5. Add Size records (label and system), then add VariantSize rows for each sellable size. Each gets its own unique SKU.
6. Open the size SKU and add Inventory for an active warehouse Location. `on_hand` is total physical stock; `reserved` is managed by checkout. Available stock is physical minus reserved. Store-only inventory does not become delivery stock.
7. Check pricing, images, sizes and stock in staging before switching the Product to Published. The current storefront does not provide an authenticated draft preview; keep draft review in Admin and use a separate staging catalogue for storefront review.

Images accept still JPEG, PNG and WebP, up to 8 MB and 25 million pixels. Product images retain the validated original and generate WebP display images up to 2,000 pixels wide, plus smaller renditions. Thumbnails and previews are visible inline; dimensions are recorded automatically. Original files are retained for merchant use, while rendered files strip image metadata. Old uploads are not automatically deleted when replaced: include storage retention and orphan cleanup in operations.

Product options include **Is best seller**, **Is new**, **Is featured**, **Is limited**, **See price in bag**, and **Max card swatches**. Scheduled Badge rows override the default badge. A sale badge takes precedence on the current card. Colour selection updates the card's image, price, availability and product link together; additional swatches expand without navigation.

## Inventory import/export

Product list actions export selected catalogue records to CSV. Spreadsheet formula prefixes are escaped. Inventory CSV imports run through the management command, with this header:

```csv
sku,location,on_hand
YOUR-SIZE-SKU,your-warehouse-slug,12
```

From the backend directory, with database settings loaded:

```powershell
.venv/Scripts/python.exe manage.py import_inventory stock.csv
.venv/Scripts/python.exe manage.py import_inventory stock.csv --apply
```

The first command validates without retaining changes. The second applies the complete file in one transaction. Duplicate SKU/location rows, unknown records, negative stock and quantities below reservations are rejected. Do not edit reservation records directly. Admin also prevents an existing stock record being reassigned to another SKU/location.

## Homepage and navigation

Page Sections support ordering, active state, start/end scheduling, title, subtitle, body, image, local link, CTA and selected products. Rendered types are HERO, PRODUCT_CAROUSEL, CATEGORY_GRID, BRAND_GRID, EDITORIAL_SPLIT, NEWSLETTER, RICH_TEXT, PROMO_BANNER, REWARDS and TRUST_BAR. VIDEO and DROP_COUNTDOWN are legacy choices without renderers; do not select them for a live campaign.

Settings are plain JSON, not HTML. Hero/editorial settings can include `eyebrow`, `image_alt`, `caption`, `footnote` and `edition`. Category grid example:

```json
{"eyebrow":"FIND YOUR ROTATION","tiles":[{"title":"Men","subtitle":"Everyday favourites","href":"/men"},{"title":"Women","subtitle":"New perspectives","href":"/women"}]}
```

Use one active HERO to supply the homepage heading. Product carousels currently display up to eight published selections. Use local links such as `/shop?brand=arc`, never remote redirects. Navigation records form the main menu: parentless records are top-level entries; child records appear in the menu. Announcement records control the dismissible announcement. Site Settings control store name, shipping price/threshold, return window, demo flag and reward accrual settings.

## Orders, marketing and community

- Orders show immutable price/item snapshots, payment status and history. Allowed actions progress paid → processing → packed → shipped → delivered. Invalid transitions are rejected; operators cannot use these actions to invent payment success.
- Promotions support percentage, fixed and shipping discounts, schedule, minimum spend, membership and usage limits, with product/brand/category targeting. Test each campaign in staging.
- Reviews submitted through the API require a delivered purchase and start Pending. Approve/reject using the moderation actions to recalculate product rating totals.
- Releases link a product with a timestamp, description and image. Set both the release timestamp and product/variant purchase release time where purchases must wait.
- Return Requests record eligible owned orders and items. Updating request status does not issue a provider refund or arrange collection. Reconcile refunds in the payment provider and follow the operating procedure.
- Subscriptions store explicit newsletter/restock/release consent. Automatic marketing/stock-alert delivery and unsubscribe links are not implemented yet. Do not promise live delivery from this demonstration workflow.
- Outbox records hold account and order messages. `sent_at` and `attempts` expose delivery state; ten failed attempts require operator investigation. Payment events, reservations, rewards, analytics and audit records are read-only ledgers in Admin.

Policy copy is illustrative. Have the merchant supply and approve shipping, returns, privacy, terms and contact content before launch. The `approved` marker is recorded; it is not currently a publication gate.
