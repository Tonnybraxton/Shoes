# ============================================================
# MASTER CODEX BUILD PROMPT
# ADVANCED MULTI-BRAND SHOE E-COMMERCE PLATFORM
# Foot Locker-Inspired Architecture + Original Premium UI
# Django Commerce Backend + Django Admin + Next.js Storefront
# ============================================================

## 0. PRIMARY MISSION

You are now the principal engineer, senior UI/UX designer, senior
frontend engineer, senior backend engineer, database architect,
security engineer, QA engineer and DevOps engineer for my shoe
e-commerce project.

Build a COMPLETE, PRODUCTION-QUALITY, premium multi-brand shoe
e-commerce platform.

This is not a landing-page exercise.

This must be a genuine commerce system with:

- advanced responsive storefront
- advanced product discovery
- product variants
- colorways
- size inventories
- product-card color switching
- product detail pages
- wishlist
- shopping cart
- checkout
- orders
- customer accounts
- promotions
- reviews
- sneaker release calendar
- loyalty/rewards
- optional store pickup
- advanced search
- Django Admin
- merchandising controls
- inventory management
- homepage content management
- SEO
- analytics events
- security
- testing
- production architecture

The PRIMARY e-commerce UX reference is:

FOOT LOCKER

Use the live official Foot Locker storefront as an information-
architecture and commerce-UX reference if browsing is available.

Study functional patterns such as:

- navigation
- mega menus
- homepage merchandising
- gender shopping
- brand shopping
- category shopping
- new arrivals
- sneaker releases
- sale experience
- product grids
- faceted filtering
- sorting
- colorways
- size discovery
- store availability
- product detail architecture
- cart
- account
- order status
- rewards
- release calendar
- help center structure
- promotional storytelling
- responsive/mobile behavior

IMPORTANT COPYRIGHT / BRAND RULE:

Do NOT copy:

- Foot Locker logo
- Foot Locker trademarks
- proprietary images
- campaign photography
- written advertising copy
- videos
- icons unique to their brand
- exact typography
- exact colors
- exact pixel dimensions
- source code
- CSS
- HTML
- protected graphic assets
- a pixel-for-pixel recreation of their visual trade dress

Instead:

RECREATE THE FUNCTIONAL DEPTH,
INFORMATION ARCHITECTURE,
MERCHANDISING LOGIC,
CONVERSION PATTERNS,
AND INTERACTION QUALITY

inside a completely ORIGINAL premium sneaker-store design system.

Our website should feel as mature as Foot Locker,
but it must visibly be its own product.

Secondary inspiration may be taken from:

- Kith: premium editorial merchandising
- END.: large multi-brand catalog architecture
- On: clean shoe presentation
- HOKA: footwear usability
- Nike: campaign storytelling
- GOAT: sneaker-drop experience
- SSENSE: minimalist product grids

Again: inspiration only.

Do not reproduce their protected assets.

---

# 1. USE THE INSTALLED CODEX SKILLS

Before implementing anything, inspect:

CODEX_SKILLS_MANIFEST.md

Use the installed skills whenever appropriate.

Expected skills include:

1. Senior Architect
2. UI/UX Pro Max
3. Frontend Design
4. Senior Frontend
5. Vercel React Best Practices
6. Database Schema Designer
7. Senior Backend
8. Senior Fullstack
9. Security & Hardening
10. Senior Security
11. Senior QA
12. Playwright
13. Senior DevOps

If their installed names differ slightly, locate the corresponding
SKILL.md files.

Read the relevant skill instructions before executing each major phase.

Recommended order:

Senior Architect
        ↓
UI/UX Pro Max
        ↓
Frontend Design
        ↓
Senior Frontend
        ↓
React Best Practices
        ↓
Database Schema Designer
        ↓
Senior Backend
        ↓
Senior Fullstack
        ↓
Security
        ↓
Senior QA
        ↓
Playwright
        ↓
DevOps

Do not merely say you are using the skills.

Actually apply their guidance.

---

# 2. DO NOT BLINDLY REBUILD AN EXISTING PROJECT

Before writing code:

1. inspect the repository
2. inspect package files
3. inspect Python dependencies
4. inspect Git status
5. inspect existing architecture
6. inspect existing components
7. inspect existing Django apps
8. inspect database configuration
9. inspect environment files
10. inspect existing product system
11. inspect tests
12. inspect README
13. inspect Docker files
14. identify reusable code

If an existing implementation is good:

KEEP AND IMPROVE IT.

Do NOT unnecessarily destroy working functionality.

Never perform destructive database resets without a legitimate need.

Do not delete user-created files.

Make incremental, reviewable changes.

---

# 3. TECHNOLOGY ARCHITECTURE

Unless the existing project already has an equally suitable architecture,
use the following.

## Frontend

Use latest compatible stable releases of:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui where appropriate
- Framer Motion for meaningful interactions
- Lucide icons
- TanStack Query where useful
- React Hook Form
- Zod

Do not install animation libraries merely for visual gimmicks.

GSAP may only be introduced where Framer Motion/CSS cannot reasonably
provide the requested interaction.

## Backend

Use:

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery where asynchronous tasks provide real value
- Django Admin

## Infrastructure

Provide support for:

- Docker Compose
- PostgreSQL
- Redis
- backend service
- frontend service
- Celery worker
- optional Celery Beat
- reverse proxy configuration
- object storage abstraction
- production environment variables

Development can use local storage.

Production should support S3-compatible object storage.

## Architecture

Use a headless-commerce pattern:

NEXT.JS STOREFRONT
        ↓
   SECURE API
        ↓
DJANGO / DRF COMMERCE CORE
        ↓
POSTGRESQL + REDIS
        ↓
DJANGO ADMIN
        ↓
MERCHANDISING / INVENTORY / ORDERS

The customer storefront must never depend upon hard-coded product
objects inside React components.

Django/PostgreSQL must be the source of truth.

---

# 4. PROJECT ORGANIZATION

Prefer a clean structure similar to:

/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   ├── services/
│   ├── styles/
│   ├── types/
│   └── tests/
│
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── catalog/
│   │   ├── inventory/
│   │   ├── merchandising/
│   │   ├── search/
│   │   ├── cart/
│   │   ├── checkout/
│   │   ├── orders/
│   │   ├── payments/
│   │   ├── promotions/
│   │   ├── reviews/
│   │   ├── wishlist/
│   │   ├── rewards/
│   │   ├── releases/
│   │   ├── stores/
│   │   ├── shipping/
│   │   ├── returns/
│   │   ├── notifications/
│   │   └── analytics/
│   ├── tests/
│   └── manage.py
│
├── infrastructure/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md

Adjust if the existing repository has a better organization.

Avoid unnecessary microservices.

Use a modular monolith until scale genuinely requires separation.

---

# 5. ORIGINAL VISUAL DIRECTION

Create an ORIGINAL premium sneaker-store identity.

The design should feel:

- premium
- bold
- youthful
- modern
- clean
- athletic
- fashion-forward
- trustworthy
- editorial
- highly polished

Do not create a generic Bootstrap/Shopify-looking storefront.

## Base aesthetic

Use:

- generous whitespace
- strong typography
- large shoe photography
- restrained borders
- premium product presentation
- clear hierarchy
- subtle depth
- subtle gradients
- elegant shadows
- tasteful motion
- polished hover states

Use Liquid Glass only selectively for:

- sticky navigation
- search overlay
- filter drawer
- mini-cart
- quick-view sheet

Do NOT make every component glass.

Shoes remain the visual focus.

## Design tokens

Create central tokens for:

- typography
- background
- surface
- foreground
- muted foreground
- border
- accent
- success
- warning
- danger
- radius
- spacing
- shadows
- animation easing
- animation durations
- z-index layers

Support:

- light mode as primary
- optional dark mode if it enhances the design

Maintain WCAG AA contrast.

---

# 6. GLOBAL WEBSITE STRUCTURE

Implement the following top-level destinations.

HOME

MEN
├── All Shoes
├── New Arrivals
├── Sneakers
├── Lifestyle
├── Running
├── Basketball
├── Football / Soccer
├── Training
├── Skate
├── Boots
├── Slides
├── Sale
└── Shop by Brand

WOMEN
├── All Shoes
├── New Arrivals
├── Sneakers
├── Lifestyle
├── Running
├── Training
├── Basketball
├── Boots
├── Slides
├── Sale
└── Shop by Brand

KIDS
├── All Kids
├── Big Kids
├── Little Kids
├── Infant / Toddler
├── Basketball
├── Lifestyle
├── Running
├── School
└── Sale

NEW ARRIVALS

RELEASES

BRANDS

COLLECTIONS

BEST SELLERS

SALE

SEARCH

WISHLIST

CART

CHECKOUT

MY ACCOUNT

ORDER TRACKING

REWARDS

RETURNS

HELP

OPTIONAL STORE LOCATOR

---

# 7. ANNOUNCEMENT / UTILITY HEADER

At the top, implement an admin-controlled promotional utility bar.

It must support:

- one or multiple rotating messages
- optional links
- scheduling
- start/end time
- country targeting
- dismiss option
- campaign tracking
- mobile behavior

Possible messages:

Free delivery threshold
New releases
Promo code
Member bonus
Return policy

Do not hard-code them.

They must come from Django Admin.

---

# 8. PRIMARY NAVIGATION

Create a premium sticky responsive navbar.

Desktop:

LOGO

Men
Women
Kids
New Arrivals
Releases
Brands
Sale

and right-side utilities:

Search
Store/Pickup optional
Wishlist
Account
Cart

## Mega menu

Mega menus should open quickly and feel intentional.

Each can contain:

- categories
- featured collections
- trending shoes
- shop by sport
- shop by brand
- editorial tile
- promotional image
- new arrivals
- best sellers

Content must be configurable from Django Admin.

Do not hardcode mega-menu campaigns.

## Mobile navigation

Build a genuine mobile navigation experience.

Include:

- full-screen or drawer navigation
- accordion categories
- nested menu support
- search
- account
- wishlist
- cart
- releases
- promotions

Ensure excellent touch targets.

---

# 9. ADVANCED SEARCH

Search is a major feature.

Implement:

- instant suggestions
- product suggestions
- brand suggestions
- category suggestions
- recent searches
- popular searches
- typo tolerance where practical
- SKU search
- model search
- colorway search
- keyboard navigation
- empty-state suggestions
- highlighted matched terms

Search overlay should be fast and premium.

Suggested layout:

┌──────────────────────────────────────────┐
│ Search shoes, brands, styles...          │
├──────────────────────────────────────────┤
│ Recent Searches                         │
│ Trending                                │
│                                         │
│ Suggested Products                      │
│ [img] Product               Price        │
│ [img] Product               Price        │
└──────────────────────────────────────────┘

Start with PostgreSQL full-text/trigram capabilities where appropriate.

Design a search abstraction so a dedicated search engine can be added
later without rewriting the storefront.

---

# 10. HOMEPAGE

Build an advanced merchandising homepage.

ALL homepage sections must be controllable through Django Admin.

Recommended sequence:

1. Announcement bar
2. Navbar
3. Hero campaign
4. Featured categories
5. Trending products
6. Shop by brand
7. New releases
8. Editorial campaign
9. Best sellers
10. Shop by sport/style
11. Limited drops
12. Personalized/recently viewed when available
13. Secondary campaign
14. Rewards
15. Customer trust section
16. Newsletter
17. Footer

## Hero

Support:

- image
- responsive image
- video
- headline
- supporting copy
- primary CTA
- secondary CTA
- text alignment
- light/dark text mode
- overlay intensity
- start/end scheduling
- audience/category targeting

Admin must control these fields.

Do not bake hero content into React.

## Homepage Page Builder

Create structured section types.

Examples:

HERO
PRODUCT_CAROUSEL
CATEGORY_GRID
BRAND_GRID
EDITORIAL_SPLIT
VIDEO
DROP_COUNTDOWN
PROMO_BANNER
REWARDS
TRUST_BAR
RICH_TEXT
NEWSLETTER

Admin can:

- enable/disable
- reorder
- schedule
- configure content
- preview

Do not allow arbitrary unsafe HTML/JavaScript injection.

---

# 11. PRODUCT CATALOG / PLP

This is one of the most important screens.

Desktop layout:

Breadcrumb
Title + result count
Category chips
Sort

Filters | Product grid
Filters | Product grid
Filters | Product grid

Mobile:

Title
Filter button
Sort button
Product grid

## Required filters

Support relevant combinations of:

- availability
- pickup availability
- gender
- age group
- brand
- category
- collection
- model
- shoe size
- color
- price
- sport
- style
- customer rating
- sale
- promotion eligible
- free shipping
- new arrival
- best seller
- limited release

Filters must:

- use URL query parameters
- survive refresh
- support deep links
- update result counts
- show active filter chips
- have clear-all
- be accessible
- work on mobile

Do not reload the full page unnecessarily.

## Sorting

Support:

- Featured
- Most Popular
- Newest
- Best Selling
- Customer Rating
- Price Low → High
- Price High → Low
- Name A → Z

Admin merchandising rank must be respected for Featured.

---

# 12. PRODUCT CARD — CRITICAL FEATURE

This is a mandatory requirement from the visual reference previously
provided by me.

Cards must contain:

PRODUCT IMAGE

COLOR SWATCHES

OPTIONAL MERCHANDISING BADGE

PRODUCT NAME

PRODUCT SUBTYPE / CATEGORY

PRICE

OPTIONAL SALE PRICE

OPTIONAL "SEE PRICE IN BAG"

RATING

OPTIONAL REVIEW COUNT

WISHLIST BUTTON

## Example

┌─────────────────────────────┐
│                        ♡    │
│                             │
│         SHOE IMAGE          │
│                             │
│                             │
├─────────────────────────────┤
│ ●  ●  ●  ●  +3             │
│                             │
│ Best Seller                 │
│ Sabrina Example             │
│ Basketball Shoes            │
│ KSh XX,XXX                  │
└─────────────────────────────┘

## COLOR-SWATCH BEHAVIOR

This is NON-NEGOTIABLE.

A product represents a shoe model.

Each product can have multiple COLORWAYS.

When a user clicks/taps a swatch:

1. set active colorway
2. update displayed shoe image
3. smoothly crossfade image
4. update variant data
5. update price if variant pricing differs
6. update sale price if relevant
7. update availability
8. update visible color name where appropriate
9. update card's accessible label
10. keep card layout stable

Do NOT trigger a full-page navigation merely because a swatch changed.

Swatches must use real buttons and ARIA labels:

"Select Black / White colorway"

Do not use color alone as the accessibility label.

## +N swatches

If more than the configured number is available:

● ● ● ● +4

Clicking +4 can:

- expand colors
or
- open quick view

Make behavior consistent.

## Hover behavior

Desktop:

hover image can reveal alternate image
such as:

- lateral view
- medial view
- lifestyle image

Do not create distracting rotations.

Mobile:

support swipe where appropriate.

## Image loading

Prefetch small variant preview assets.

Do not download every full-resolution variant image up front.

## Quick view

Optional quick-view drawer/modal:

- gallery
- colors
- sizes
- price
- stock
- wishlist
- link to full PDP

Never allow quick add without requiring a valid size.

---

# 13. DJANGO ADMIN MUST CONTROL PRODUCT CARDS

Django Admin is not an afterthought.

It is the operational control center.

For every product, administrators must be able to control:

- title
- slug
- brand
- categories
- collections
- gender
- age range
- sport
- style
- description
- status
- publication date
- featured status
- best seller status
- new arrival status
- limited status
- exclusive status
- sale status
- merchandising priority
- searchable keywords
- SEO metadata

## Product-card presentation controls

Admin must control:

- card badge
- badge text
- badge type
- badge priority
- badge start/end dates
- default colorway
- swatch display order
- maximum visible swatches
- default card image
- alternate hover image
- price display mode
- "See Price in Bag" mode
- promotional message
- featured ordering
- card visibility
- scheduled publication

Do not allow unsafe arbitrary CSS through Admin.

Use a safe enumeration for supported presentation modes.

## Admin image preview

Show product thumbnails inside Django Admin.

Provide previews for:

- default image
- hover image
- variant images
- swatches

## Product preview

Provide an admin-only preview route.

Admin should be able to preview:

- product card
- product page
- unpublished products

before publishing.

---

# 14. CATALOG DATA MODEL

Design this carefully before migrations.

## Brand

Fields approximately:

id
name
slug
description
logo
hero_image
website_optional
is_active
sort_order
seo_title
seo_description

## Category

Support hierarchical categories.

Fields:

id
parent
name
slug
description
image
gender_scope
sort_order
is_active

## Product

Represents a model/style family.

Fields:

id
brand
name
slug
subtitle
description
gender
age_group
sport
style
base_price
compare_at_price
status
release_date
is_new
is_featured
is_best_seller
is_limited
is_exclusive
rating_cached
review_count_cached
merchandising_score
seo_title
seo_description
created_at
updated_at

Do not depend solely on booleans if scheduled merchandising is needed.

## ProductVariant

Represents a colorway / SKU group.

Fields:

id
product
sku
color_name
color_code
color_family
price_override
compare_at_price_override
release_date
is_active
is_default
sort_order
barcode_optional

## ProductImage

Fields:

variant
image
alt_text
view_type

view_type options:

PRIMARY
LATERAL
MEDIAL
TOP
REAR
SOLE
DETAIL
LIFESTYLE
HOVER
360_FRAME

plus:

sort_order
width
height

## Size

Support multiple systems:

US Men
US Women
UK
EU
Kids

Do not store size only as uncontrolled strings.

## VariantSize / SKU inventory

Map:

variant
size
inventory

Use an appropriate structure to represent sellable SKU combinations.

## Inventory

Track:

- on hand
- reserved
- available
- low-stock threshold
- incoming optional
- warehouse/store

Prevent overselling using transactional locking/atomic operations.

---

# 15. PRODUCT DETAIL PAGE

Build a premium PDP.

Desktop:

┌──────────────────────────┬───────────────────────┐
│                          │ Brand                 │
│                          │ Product title         │
│     PRODUCT GALLERY      │ Rating                │
│                          │ Price                 │
│                          │ Color                 │
│                          │ Swatches              │
│                          │                       │
│                          │ Select Size           │
│                          │ Size Guide            │
│                          │                       │
│                          │ Delivery              │
│                          │ Pickup optional       │
│                          │                       │
│                          │ ADD TO BAG            │
│                          │ Wishlist              │
└──────────────────────────┴───────────────────────┘

Then:

Product story
Technology/features
Fit guidance
Delivery
Returns
Reviews
Questions optional
Related products
Recently viewed

## Product gallery

Support:

- thumbnails
- swipe
- image zoom
- keyboard navigation
- fullscreen viewer
- variant-aware images
- optional video
- optional 360 image sequence

## Color selection

Changing PDP color:

- changes selected variant
- changes gallery
- changes SKU
- changes stock
- changes price if relevant
- changes size availability
- can update URL state

## Size selection

Show:

Available
Low stock
Unavailable

Do not allow unavailable sizes to be selected.

Provide:

- size guide
- size conversion
- fit notes
- "notify me when available"

## Sticky purchase CTA

Mobile:

use a polished sticky purchase CTA once the principal controls scroll
out of view.

It must never obscure essential content.

---

# 16. FIT / SIZE ASSISTANT — IMPROVEMENT

Add an optional fit helper.

Do not make medical or biometric claims.

Allow a customer to select:

- usual shoe size
- size system
- preferred fit: snug / regular / roomy
- previously worn model optional

Return an understandable recommendation.

Keep logic explainable.

Admin can configure product-specific:

- runs small
- true to size
- runs large
- narrow
- standard
- wide

Use customer review fit feedback later.

---

# 17. WISHLIST

Implement:

- anonymous/local wishlist support where reasonable
- authenticated persistent wishlist
- merge local wishlist after login
- heart button on cards/PDP
- wishlist page
- move to cart
- remove
- stock status
- price changes
- shareable wishlist optional

---

# 18. RECENTLY VIEWED

Track locally for guests.

For authenticated users, optionally synchronize.

Show:

- recently viewed carousel
- return-to-product shortcuts

Respect privacy settings.

---

# 19. CART

Build a premium cart drawer plus cart page.

Cart item displays:

- image
- brand
- product
- color
- size
- quantity
- price
- discount
- stock warning

Functions:

- change quantity
- remove
- move to wishlist
- edit size/color
- promo code
- shipping estimate
- subtotal
- savings
- tax estimate where applicable
- rewards redemption if enabled

Cart must validate prices and stock on server.

Never trust browser totals.

## Inventory reservation

Design safe reservation logic.

When checkout begins, inventory can be reserved for a short controlled
period where appropriate.

Use transactional safeguards.

---

# 20. CHECKOUT

Support guest checkout.

Do not require account creation before purchase.

Checkout steps:

1. contact information
2. shipping address
3. delivery method
4. pickup option where configured
5. promotions / rewards / gift cards
6. payment
7. order review
8. confirmation

Provide:

- inline validation
- mobile keyboard optimization
- progress indicator
- accessible errors
- persistent cart
- no surprise costs

## Payments

Implement a provider abstraction.

Support at least:

PAYMENT_PROVIDER interface

and one properly integrated sandbox/test provider if credentials and
project scope permit.

Make architecture expandable to:

- Stripe
- PayPal
- M-Pesa/Daraja
- other regional providers

For Kenyan deployment, M-Pesa can be enabled through environment
configuration.

NEVER:

- hardcode production credentials
- store raw card numbers
- invent payment success
- mark order paid before provider verification

Use:

- webhooks
- signature verification
- idempotency
- transaction records
- retry-safe handlers

Provide a mock/test payment provider for automated development tests
only, clearly marked non-production.

---

# 21. ORDERS

Order state machine approximately:

PENDING
PAYMENT_PENDING
PAID
PROCESSING
PACKED
SHIPPED
READY_FOR_PICKUP
DELIVERED
CANCELLED
REFUND_PENDING
REFUNDED
RETURN_REQUESTED
RETURNED

Do not allow arbitrary impossible transitions.

Order stores snapshots of:

- product name
- SKU
- color
- size
- unit price
- discounts
- tax
- customer address

so historic orders remain valid if catalog data changes.

---

# 22. ORDER TRACKING

Provide:

MY ACCOUNT → ORDERS

and guest order lookup using secure identifiers.

Display timeline:

ORDER CONFIRMED
      ↓
PROCESSING
      ↓
PACKED
      ↓
SHIPPED
      ↓
OUT FOR DELIVERY
      ↓
DELIVERED

Never expose another customer's order from guessable IDs.

---

# 23. EMAIL / NOTIFICATIONS

Generate transactional templates for:

- account welcome
- email verification
- password reset
- order received
- payment confirmation
- shipment confirmation
- ready for pickup
- delivery confirmation
- return confirmation
- refund confirmation
- back-in-stock
- release reminder

Use asynchronous tasks for emails where practical.

Development mode should safely use a console/local mail backend.

---

# 24. REVIEWS

Implement verified-purchase aware reviews.

Fields:

- rating
- title
- body
- fit feedback
- comfort optional
- verified purchase
- status
- moderation reason
- created date

Admin moderation:

PENDING
APPROVED
REJECTED

Product pages show:

- average rating
- distribution
- review count
- recent reviews
- fit feedback

Protect against spam and duplicate abuse.

---

# 25. ADVANCED RELEASE CALENDAR

Create a dedicated sneaker release experience inspired by mature
sneaker retailers.

Routes:

/releases
/releases/upcoming
/releases/released
/releases/[slug]

Calendar supports:

- release date
- release time
- timezone
- countdown
- brand
- gender
- age range
- image
- retail price
- sizes
- coming soon
- just launched
- sold out
- entry open
- entry closed

Filters:

- brand
- gender
- age group
- month
- availability
- release type

## Drop countdown

Example:

JORDAN EXAMPLE RELEASE

04 DAYS : 11 HRS : 32 MIN : 08 SEC

[ VIEW RELEASE ]

Countdown must use server release time and handle timezones correctly.

---

# 26. DROP ENTRY / RAFFLE — ADVANCED IMPROVEMENT

Design as feature-flagged functionality.

Administrators can create:

- first-come-first-served release
- online draw
- store-pickup draw
- standard release

A draw can define:

- entry start
- entry end
- available sizes
- eligible locations
- quantity
- customer eligibility rules

Prevent duplicate entries.

Keep auditable selection records.

Never claim randomness/fairness unless implemented and verifiable.

This feature can remain disabled until the store wants to run drops.

---

# 27. LOYALTY / REWARDS

Create our OWN reward program.

Do NOT copy the FLX name, tier names or branding.

Example temporary name:

SOLE CLUB

Make name configurable.

Features:

- free membership
- points
- tiers
- member-only offers
- birthday reward optional
- free shipping threshold/perk
- early release access optional
- reward vouchers
- reward history

Admin controls:

- points-per-currency unit
- tiers
- reward thresholds
- promotions
- expiration rules
- member campaigns

All point mutations must be ledger-based and auditable.

Never store only a mutable points number without history.

---

# 28. PROMOTIONS ENGINE

Support:

- percentage discount
- fixed discount
- category discount
- brand discount
- product discount
- BOGO where needed
- free shipping
- member-only
- promo code
- automatic promotion
- scheduled campaign

Rules can include:

- start/end
- usage limit
- per-user limit
- minimum cart value
- selected brands
- selected products
- excluded products
- user segments

Discount calculations happen server-side.

---

# 29. "SEE PRICE IN BAG"

This was part of the card behavior I want available.

Implement as an admin-controlled price-display mode.

NORMAL
SALE
SEE_PRICE_IN_BAG

If SEE_PRICE_IN_BAG:

catalog displays:

"See Price in Bag"

but internal pricing rules remain server controlled.

Do not use it to deceive customers.

At cart time, clearly show the actual price.

---

# 30. GIFT CARDS — OPTIONAL ADVANCED FEATURE

Architecture should support:

- digital gift cards
- secure random code
- PIN/token
- balance
- transaction ledger
- expiration rules where legally applicable
- partial redemption
- email delivery

Do not implement weak predictable gift-card codes.

Feature flag if not needed for initial launch.

---

# 31. STORES AND PICKUP — OPTIONAL BUT BUILT CORRECTLY

Create:

Store
StoreHours
StoreInventory

Allow users to SEARCH by:

- city
- postal code
- town
- region

Do not require precise GPS permission.

Display:

- address
- distance where calculable
- opening hours
- stock
- pickup eligibility

Workflow:

Choose store
    ↓
Choose product
    ↓
Choose variant
    ↓
Choose size
    ↓
Validate inventory
    ↓
Add as pickup order
    ↓
Confirmation
    ↓
Ready notification

Feature should automatically disappear if no stores exist.

---

# 32. CUSTOMER ACCOUNT

Dashboard:

Overview
Orders
Wishlist
Addresses
Rewards
Notifications
Saved preferences
Recently viewed
Returns
Profile
Security

Account features:

- register
- sign in
- sign out
- password reset
- email verification
- profile update
- address management

Use secure HTTP-only authentication patterns.

Never store auth tokens in localStorage if a safer architecture is
available.

---

# 33. AUTHORIZATION

Customer roles:

CUSTOMER

Operational Django roles:

CONTENT_EDITOR
MERCHANDISER
INVENTORY_MANAGER
ORDER_MANAGER
CUSTOMER_SUPPORT
MARKETING_MANAGER
ADMIN
SUPERUSER

Use Django Groups/Permissions or a similarly robust permission model.

Examples:

Merchandiser:
products + collections + homepage

Inventory manager:
stock but not payment settings

Support:
orders/returns but not system secrets

Marketing:
campaigns/rewards/promotions

Apply least privilege.

---

# 34. DJANGO ADMIN — FULL OPERATIONS CENTER

The Django Admin is REQUIRED.

The backend must be comfortable to operate without editing source code.

## Dashboard workflows

Provide management interfaces for:

### Catalog
- Products
- Brands
- Categories
- Collections
- Variants
- Colors
- Sizes
- Product images

### Merchandising
- Homepage sections
- Hero campaigns
- Promotional banners
- Navigation
- Mega menus
- Badges
- Featured products
- Sort priorities

### Commerce
- Carts where appropriate
- Orders
- Payments
- Shipments
- Returns
- Refund records

### Marketing
- Promotions
- Coupons
- Releases
- Rewards
- Gift cards if enabled

### Community
- Reviews
- back-in-stock subscriptions

### Operations
- Stores
- inventory
- stock adjustments

## Admin quality

Use:

- search_fields
- list_filter
- autocomplete_fields
- prepopulated_fields
- readonly_fields
- fieldsets
- tabular/stacked inlines
- date hierarchy
- bulk actions
- optimized queries
- image thumbnails

Avoid N+1 queries inside Admin lists.

## Product admin

The product screen should make managing a shoe intuitive.

PRODUCT
│
├── General
├── Classification
├── Merchandising
├── SEO
├── Variants
│    ├── Mint/Black
│    ├── Pink/Green
│    └── Black/Grey
│
├── Images
├── Sizes
├── Inventory
└── Preview

Implement robust inline workflows where appropriate.

---

# 35. BULK PRODUCT MANAGEMENT

Add advanced admin functionality for:

- bulk publish/unpublish
- set featured
- set best seller
- assign collection
- schedule promotion
- update merchandising rank
- export catalog
- import structured CSV

Use validation.

Never silently overwrite invalid SKUs.

For imports:

- preview
- validation report
- transaction
- failure rollback

Prefer a proven library if needed, after verifying compatibility.

---

# 36. PRODUCT MEDIA

Use an image pipeline.

Store original.

Generate responsive versions.

Serve appropriate sizes.

Prefer:

- AVIF where supported
- WebP fallback
- JPEG/PNG when needed

Preserve original aspect ratio.

Prevent layout shifts.

ProductCard should never load giant PDP imagery.

Generate appropriate:

- thumbnail
- card
- card retina
- PDP medium
- PDP large

Use descriptive alt text.

Do not scrape copyrighted product photography from competitors.

Seed with neutral placeholders if licensed product imagery is not
available.

---

# 37. BRAND DIRECTORY

Create:

/brands

with:

- A–Z navigation
- search
- featured brands
- logo grid
- brand cards

Each brand page:

Hero
Description
Featured shoes
New arrivals
Best sellers
Collections
All products

Brands should be data-driven.

---

# 38. COLLECTIONS

Support editorial collections such as:

Trending
Back to School
Running Essentials
Basketball
Retro
Minimal Sneakers
Summer Rotation
New Season

Collections can be:

- manually curated
- rules-based
- scheduled

Admin manages collection presentation.

---

# 39. IMPROVED SHOPPING DISCOVERY

Add features that improve on the reference experience.

## Product comparison

Allow 2–4 shoes to be compared.

Compare:

- price
- sport
- weight if available
- cushioning
- fit
- sizes
- colors
- customer rating
- stock

## Restock notification

Customer chooses:

color + size

Then enters email or uses account.

Notify only when that exact SKU returns.

## Price-drop alerts

Optional account setting.

## Recently viewed

Already defined.

## Similar products

Initially use explainable rules:

same brand
same category
similar price
similar sport/style
available stock

Do not introduce expensive AI infrastructure merely to call the feature
"AI."

---

# 40. PERSONALIZATION — PRIVACY-FIRST

For consenting returning users, personalize:

- recently viewed
- preferred brands
- preferred gender category
- saved sizes
- recommendation sections

Provide controls.

Do not fingerprint users.

Do not create creepy personalization.

---

# 41. MOBILE FIRST-CLASS EXPERIENCE

Do not make desktop first and merely shrink it.

Optimize:

- navbar
- menus
- swatches
- gallery
- filter sheet
- sort sheet
- size selector
- cart
- checkout
- sticky CTA
- search
- release calendar

Targets:

320px+
375px
390px
430px
tablet
desktop
wide desktop

Ensure no horizontal overflow.

---

# 42. MOTION SYSTEM

Motion must communicate state.

Examples:

Card swatch:
150–250ms crossfade

Mega menu:
subtle fade/translate

Cart drawer:
spring/sliding transition

Wishlist:
small confirmation state

Product gallery:
smooth but immediate

Page transitions:
only where performance remains good

Respect:

prefers-reduced-motion

Never create:

- excessive parallax
- cursor hijacking
- long loading animations
- motion that blocks purchase
- scroll-jacking

---

# 43. ACCESSIBILITY

Target WCAG 2.2 AA.

Must include:

- skip navigation
- semantic landmarks
- correct heading hierarchy
- keyboard navigation
- visible focus
- accessible dialogs
- accessible drawers
- ARIA labels
- accessible swatches
- alt text
- form errors tied to fields
- color contrast
- reduced motion
- adequate touch targets

Product-card swatches must work entirely by keyboard.

Run automated accessibility checks with Playwright/axe if installed.

Also perform manual semantic review.

---

# 44. SEO

Implement strong technical SEO.

Every indexable product:

- unique title
- meta description
- canonical URL
- OpenGraph
- Twitter metadata
- Product structured data
- Offer structured data
- AggregateRating when legitimate
- breadcrumbs structured data

Create:

- sitemap
- robots.txt
- category metadata
- brand metadata
- release metadata

Handle variant URLs without duplicate-content problems.

Do not place fake reviews in structured data.

---

# 45. PERFORMANCE

Use the installed Vercel React Best Practices skill.

Targets should be ambitious but realistic.

Optimize:

- LCP
- CLS
- INP
- server response
- bundle size

Strategies:

- optimized image sizes
- lazy loading
- route-level code splitting
- caching
- request deduplication
- avoid client components unless necessary
- avoid large animation packages everywhere
- avoid waterfall data fetching
- server rendering where beneficial
- pagination or controlled infinite loading

Do not fetch:

all products
all colors
all full-size images
all reviews

on initial homepage load.

---

# 46. CACHING

Use Redis where appropriate.

Candidates:

- category configuration
- brand lists
- homepage section structure
- popular search suggestions
- product summaries
- inventory reads with careful invalidation

Never cache volatile stock indefinitely.

Invalidate on relevant admin updates.

---

# 47. INVENTORY CONCURRENCY

This is critical.

When two customers try buying the last pair:

DO NOT oversell.

Use:

- transactions
- row-level locking where appropriate
- reserved quantities
- idempotent checkout/order creation

Test this behavior.

---

# 48. SECURITY

Apply the installed Security skills.

Required:

- secure headers
- HTTPS assumptions
- CSRF protection
- XSS prevention
- ORM-safe queries
- input validation
- secure cookies
- session fixation prevention
- least privilege
- rate limits
- account lockout/throttling where appropriate
- password hashing
- secret management
- webhook signatures
- upload validation
- audit logging for sensitive Admin activity

Never:

- commit `.env`
- log passwords
- log payment credentials
- expose stack traces in production
- trust client price/discount data

Django Admin production protection should include:

- non-default secret configuration
- staff permissions
- optional 2FA when a maintained compatible solution is available
- rate limiting/proxy protection
- HTTPS
- secure cookies

---

# 49. API DESIGN

Use versioned routes where appropriate.

Examples:

/api/v1/products/
/api/v1/products/{slug}/
/api/v1/brands/
/api/v1/categories/
/api/v1/search/
/api/v1/releases/
/api/v1/wishlist/
/api/v1/cart/
/api/v1/checkout/
/api/v1/orders/
/api/v1/reviews/
/api/v1/rewards/

Use:

- consistent errors
- pagination
- filters
- validation
- HTTP semantics
- permissions
- throttling

Do not expose Django model internals directly.

Create intentional serializers/contracts.

---

# 50. API ERROR FORMAT

Use a predictable shape such as:

{
  "error": {
    "code": "OUT_OF_STOCK",
    "message": "This size is no longer available.",
    "fields": {}
  }
}

Do not leak server internals.

---

# 51. DATABASE QUALITY

Use the Database Schema Designer skill.

Requirements:

- proper indexes
- unique constraints
- foreign keys
- CHECK constraints where useful
- appropriate decimal money fields
- timezone-aware datetimes
- soft deletion only where it provides clear value
- audit fields
- migration safety

Never use float for money.

Add indexes based on real access patterns.

---

# 52. ANALYTICS EVENTS

Create an analytics abstraction.

Track first-party commerce events:

view_home
view_item_list
select_item
view_item
select_color
select_size
add_to_wishlist
add_to_cart
remove_from_cart
view_cart
begin_checkout
add_shipping_info
add_payment_info
purchase
search
apply_filter
view_release
enter_release

Do not bind application logic directly to one analytics provider.

Respect consent requirements.

---

# 53. ADMIN ANALYTICS

Provide useful commerce summaries in a safe operational dashboard or
documented report endpoint:

- revenue
- orders
- average order value
- units sold
- top products
- top brands
- low stock
- refund count
- release performance

Do not build misleading vanity metrics.

If full dashboards create excessive scope, build clean service/query
layers first and expose essential Admin views.

---

# 54. ERROR / EMPTY STATES

Design polished states for:

- no search results
- no filtered results
- empty cart
- empty wishlist
- no order history
- no releases
- unavailable size
- out of stock
- payment failure
- connection problem
- 404
- 500

Every state should suggest a next action.

---

# 55. LOADING STATES

Use:

- skeleton cards
- image placeholders
- button progress states
- checkout progress

Avoid giant spinners.

Prevent double-submit on payment/order forms.

---

# 56. FOOTER

Build a comprehensive footer.

Sections can include:

SHOP
Men
Women
Kids
New
Releases
Sale

HELP
Contact
Shipping
Returns
Size Guide
Order Status
FAQ

ACCOUNT
Sign In
Register
Orders
Wishlist
Rewards

ABOUT
Our Story
Careers optional
Accessibility
Sustainability optional

LEGAL
Privacy
Terms
Cookies
Accessibility

SOCIAL

NEWSLETTER

Django Admin should manage configurable footer navigation where
practical.

---

# 57. HELP CENTER

Implement structured pages for:

- Account Help
- Ordering
- Shipping
- Store Pickup
- Returns / Exchanges
- Gift Cards if enabled
- Product & Sizing
- Payments
- Contact
- FAQs

Use searchable FAQ data.

Admin controls content.

Do not copy Foot Locker help text.

Write original policies/placeholders requiring business approval.

---

# 58. RETURNS

Implement a return request workflow.

Customer:

Order
  ↓
Eligible item
  ↓
Reason
  ↓
Return / Exchange
  ↓
Instructions
  ↓
Tracking/status

Admin:

Requested
Approved
Label issued optional
Received
Inspected
Refunded / Exchanged
Rejected

Return policies must be configurable.

Do not hard-code Foot Locker's exact policy.

---

# 59. INTERNATIONALIZATION

Design for:

- configurable default currency
- currency display
- locale
- timezone
- address formats

Do not implement fake FX conversion.

If multiple currencies are enabled:

use explicitly configured pricing or a reliable pricing service.

Default development currency can be selected from environment/config.

Support KES cleanly.

---

# 60. KENYA-READY OPTION

Without making the architecture Kenya-only, ensure it can support:

- KES
- Nairobi and Kenyan addresses
- county/city fields where appropriate
- M-Pesa payment provider
- local delivery methods
- pickup points

These should remain configuration-driven.

---

# 61. SAMPLE DATA

Create a seed system.

Populate enough realistic DEMO data to test:

- multiple brands
- categories
- products
- colorways
- sizes
- stock levels
- new arrivals
- best sellers
- releases
- sale items
- homepage campaigns

Do NOT scrape competitor data or copyrighted images.

Use:

- generated placeholders
- developer-owned assets
- neutral demo imagery
- clearly marked sample content

Product architecture should support brands such as Nike, adidas,
Jordan, New Balance, ASICS, Puma, Converse, Vans, HOKA and On when the
store legitimately has rights to sell/represent those products.

Do not fabricate partnership claims.

---

# 62. TESTING STRATEGY

No feature is complete until tested.

## Backend

Use:

- pytest
- pytest-django
- factories where useful

Test:

- models
- serializers
- permissions
- cart calculations
- pricing
- promotions
- inventory
- checkout
- orders
- rewards
- release entries
- admin-critical services

## Frontend

Use:

- component tests
- integration tests
- accessibility tests

## Playwright

Required journeys:

### E2E 01 — Product color card

Open catalog
→ find multi-color product
→ click second swatch
→ card image changes
→ active swatch changes
→ title remains correct
→ price is correct
→ no layout shift

### E2E 02 — PDP variants

Open product
→ select color
→ gallery changes
→ available sizes change
→ select size
→ add to cart

### E2E 03 — Out of stock

Select unavailable SKU
→ purchase unavailable

### E2E 04 — Filters

Men
→ Nike
→ Basketball
→ Size
→ Black
→ Price range
→ verify products

Refresh page
→ filters remain in URL/state

### E2E 05 — Search

Search model
→ autocomplete
→ results

### E2E 06 — Wishlist

Wishlist
→ login if necessary
→ refresh
→ persists

### E2E 07 — Cart

Add product
→ quantity change
→ totals update

### E2E 08 — Checkout

Guest checkout
→ shipping
→ test payment
→ order created
→ confirmation

### E2E 09 — Account

Register
→ login
→ view orders

### E2E 10 — Release calendar

Upcoming release
→ countdown
→ detail page

### E2E 11 — Admin

Admin creates product
→ variant
→ images
→ sizes
→ stock
→ badge
→ publish
→ product appears correctly on storefront

### E2E 12 — Product card admin rendering

Admin changes:

default colorway
default image
badge
swatch order

→ storefront reflects change after cache invalidation

### E2E 13 — Mobile

Test:

375×812
390×844
430×932

Navigation
Filters
PDP
Cart
Checkout

### E2E 14 — Accessibility

Keyboard:

nav
search
filters
swatches
size selector
cart
checkout

### E2E 15 — Concurrent stock

Simulate final SKU contention.

Only valid inventory quantity can successfully complete.

---

# 63. VISUAL REGRESSION

Create screenshots for key pages:

- homepage desktop
- homepage mobile
- PLP desktop
- PLP mobile
- PDP desktop
- PDP mobile
- cart
- checkout
- release calendar
- admin product screen where feasible

Use visual regression thoughtfully.

Do not fail tests because of dynamic timestamps without normalization.

---

# 64. RESPONSIVE QUALITY GATE

Before declaring complete, inspect each key page at:

320
375
390
430
768
1024
1280
1440
1920

Check:

- clipping
- overflow
- alignment
- images
- typography
- touch size
- modal sizing
- drawer sizing
- sticky UI

---

# 65. PRODUCTION QUALITY GATE

Before final completion run relevant:

Frontend:
- formatter
- lint
- typecheck
- unit tests
- build
- Playwright

Backend:
- format/lint
- Django checks
- migration check
- unit tests
- security deployment checks where appropriate

Dependencies:
- vulnerability review

Infrastructure:
- Docker build
- service startup
- migrations
- seed test

Never report success with failing tests.

---

# 66. CI/CD

Create GitHub Actions or equivalent for:

BACKEND

Install
Lint
Test
Migration check

FRONTEND

Install
Lint
Typecheck
Test
Build

E2E

Playwright against test stack

Security

dependency audit

Do not deploy automatically to production without explicit production
credentials/approval.

---

# 67. OBSERVABILITY

Use structured logging.

Production should support:

- request ID
- user ID where lawful/appropriate
- order ID
- payment event ID
- severity
- timestamps

Never log:

- passwords
- full payment data
- authentication secrets

Provide error-monitoring integration points.

---

# 68. DEVELOPMENT EXPERIENCE

Create:

README.md

It must include:

- prerequisites
- installation
- environment setup
- Docker usage
- database setup
- migrations
- seed data
- frontend start
- backend start
- Celery start
- tests
- Admin setup
- payment sandbox
- deployment notes

Create:

.env.example

Never include real secrets.

---

# 69. DOCUMENTATION

Create:

docs/ARCHITECTURE.md
docs/DATABASE.md
docs/ADMIN_GUIDE.md
docs/STOREFRONT.md
docs/API.md
docs/SECURITY.md
docs/TESTING.md
docs/DEPLOYMENT.md

## ADMIN_GUIDE

Explain specifically:

How to add a shoe

How to add colorways

How to add shoe images

How to configure swatches

How to add sizes

How to manage stock

How to set Best Seller

How to enable See Price in Bag

How to create a release

How to create a homepage campaign

How to change mega-menu content

How to preview before publishing

---

# 70. IMPLEMENTATION PHASES

Do not attempt random changes everywhere simultaneously.

## PHASE A — Discovery

- inspect repo
- inspect skills
- inspect current UI
- identify risks
- create implementation checklist

## PHASE B — Architecture

Use Senior Architect.

Create architecture plan.

Determine:

- data boundaries
- API boundaries
- frontend architecture
- database
- caching
- auth
- payments

## PHASE C — Design system

Use:

UI/UX Pro Max
Frontend Design

Create:

- tokens
- typography
- layout grid
- buttons
- inputs
- cards
- dialogs
- sheets
- badges
- swatches
- navbar
- footer

## PHASE D — Database

Use Database Schema Designer.

Create:

catalog
variants
inventory
merchandising
commerce models

Review migrations.

## PHASE E — Backend

Use Senior Backend.

Implement:

API
auth
catalog
inventory
orders
cart
checkout
promotions
admin

## PHASE F — Storefront

Use:

Senior Frontend
React Best Practices

Implement:

home
navigation
search
PLP
ProductCard
PDP
wishlist
cart

## PHASE G — Commerce

checkout
payments
orders
shipping
emails

## PHASE H — Advanced commerce

releases
rewards
reviews
returns
pickup
restock notifications

## PHASE I — QA

Use:

Senior QA
Playwright
Security

## PHASE J — Production readiness

Use Senior DevOps.

---

# 71. DO NOT LEAVE DEAD UI

Every visible button must:

- work
or
- be intentionally disabled with an explanation

Do not create fake buttons.

Examples that MUST function if rendered:

Search
Filter
Sort
Wishlist
Color swatches
Size selection
Add to Bag
Cart quantity
Checkout
Login
Order lookup

If a feature is not implemented:

do not pretend that it is.

Use an explicit feature flag.

---

# 72. NO LOW-QUALITY SHORTCUTS

Do not:

- make everything one component
- use hard-coded arrays for production data
- ignore TypeScript errors
- suppress errors with `any`
- disable ESLint rules to make builds pass
- create fake API responses in production
- use index as key for dynamic products
- trust prices from frontend
- expose secrets
- copy competitor HTML
- hotlink competitor images
- implement fake checkout success
- create fake reviews
- add random libraries for small tasks
- leave TODOs in critical purchase flows

---

# 73. DEFINITION OF DONE — PRODUCT CARD

A ProductCard is complete only when:

[ ] It loads from backend data
[ ] Image is responsive
[ ] Wishlist works
[ ] Badge works
[ ] Price works
[ ] Sale price works
[ ] See Price in Bag works when enabled
[ ] Color swatches work
[ ] Selected swatch image changes
[ ] +N works
[ ] Hover image works
[ ] Keyboard works
[ ] Screen-reader label exists
[ ] Loading state exists
[ ] Error state exists
[ ] Mobile works
[ ] Admin controls display
[ ] Tests pass

---

# 74. DEFINITION OF DONE — PRODUCT

A Product is complete only when admin can:

[ ] Create brand
[ ] Create product
[ ] Create colorways
[ ] Upload images
[ ] Configure swatches
[ ] Create sizes
[ ] Enter inventory
[ ] Configure price
[ ] Set promotion
[ ] Add badges
[ ] Publish
[ ] Preview

and the customer can:

[ ] discover it
[ ] search it
[ ] filter it
[ ] view card
[ ] switch color
[ ] view PDP
[ ] select size
[ ] wishlist it
[ ] add it to cart
[ ] buy it

---

# 75. DEFINITION OF DONE — WEBSITE

The website is NOT complete because the homepage looks impressive.

It is complete only when:

[ ] Homepage is polished
[ ] Mega menu works
[ ] Search works
[ ] Catalog works
[ ] Filtering works
[ ] Sorting works
[ ] Product cards work
[ ] Color variants work
[ ] PDP works
[ ] Wishlist works
[ ] Cart works
[ ] Checkout works
[ ] Test payment works
[ ] Orders work
[ ] Django Admin works
[ ] Inventory works
[ ] Release calendar works
[ ] Account works
[ ] Mobile works
[ ] Accessibility passes
[ ] Security review complete
[ ] Unit tests pass
[ ] E2E tests pass
[ ] Production build passes
[ ] Documentation exists

---

# 76. FINAL POLISH — MAKE THE WEBSITE FEEL EXPENSIVE

After functionality is complete, perform a dedicated visual review.

Review:

- typography consistency
- spacing rhythm
- image cropping
- product-card height
- content density
- swatch alignment
- buttons
- hover states
- focus states
- loading skeletons
- empty states
- animation timing
- navbar
- mega menu
- filter drawer
- mobile bottom interactions
- cart
- checkout

Remove anything that feels:

- template-like
- childish
- cluttered
- excessively animated
- inconsistent
- cheap

The store should communicate:

AUTHENTICITY
QUALITY
TRUST
SNEAKER CULTURE
PREMIUM RETAIL

---

# 77. FOOT LOCKER REFERENCE AUDIT

If web/browser capability is available:

Before frontend implementation, inspect the CURRENT live Foot Locker
storefront.

Audit at minimum:

1. Homepage
2. Desktop navigation
3. Mobile navigation
4. Men's shoes
5. Women's shoes
6. Kids shoes
7. Product listing
8. Filters
9. Sort menu
10. Product cards
11. Product detail
12. Search
13. New arrivals
14. Sale
15. Brands
16. Release calendar
17. Rewards
18. Store pickup
19. Account
20. Cart
21. Checkout entry
22. Order status
23. Help center
24. Footer

Create:

docs/REFERENCE_UX_AUDIT.md

For each feature record:

REFERENCE PATTERN
WHY IT WORKS
OUR ORIGINAL IMPLEMENTATION
IMPROVEMENT

Do NOT store copyrighted screenshots in the repository unless I own or
am authorized to store them.

Do not copy CSS/HTML/source.

---

# 78. REQUIRED IMPROVEMENTS BEYOND THE REFERENCE

Our website should improve the customer experience with:

1. Better product-card color switching
2. Faster variant previews
3. Cleaner premium visual design
4. Better mobile filtering
5. Better search autocomplete
6. Saved shoe-size preference
7. Exact-size restock alerts
8. Product comparison
9. Cleaner release calendar
10. Admin-configurable storefront
11. Product preview before publication
12. More transparent availability
13. Better mobile checkout
14. Better accessibility
15. Better Core Web Vitals
16. Better structured SEO
17. Privacy-first personalization
18. Optional typed-location store pickup
19. Better inventory protection
20. Better admin bulk operations

---

# 79. ADMIN-DRIVEN RENDERING PRINCIPLE

THIS IS IMPORTANT.

I want Django Admin to control what customers see.

Do not require editing frontend code just to:

- change a hero
- add a product
- add a color
- change a card image
- add a size
- update stock
- add a badge
- mark best seller
- feature a product
- create a sale
- rearrange homepage sections
- change navigation
- schedule a campaign
- create a sneaker release

Think of Django Admin as the commerce CMS.

Next.js is the renderer.

Django controls the data and merchandising.

---

# 80. CACHE INVALIDATION

When admin changes storefront-critical data:

- product
- price
- stock
- hero
- badge
- navigation
- homepage
- promotion

changes should become visible predictably.

Implement:

- versioned cache keys
or
- targeted invalidation
or
- safe revalidation

Do not leave customers seeing stale product prices for long periods.

---

# 81. STOREFRONT PREVIEW MODE

Implement secure preview support.

Authorized staff should be able to preview:

- draft products
- scheduled campaigns
- future homepage layouts

without exposing drafts publicly.

Preview tokens must:

- expire
- be unguessable
- be permission controlled

---

# 82. SAFE CONTENT MODELS

Do not make the homepage builder an unsafe HTML editor.

Use structured models.

Example:

HomepageSection:
- type
- title
- subtitle
- image
- video
- collection
- products
- CTA
- theme
- order
- visible
- start
- end

Frontend decides how approved section types render.

This preserves consistency and security.

---

# 83. PRODUCT AVAILABILITY

Display useful status such as:

IN STOCK
LOW STOCK
SOLD OUT
COMING SOON
ONLINE ONLY
STORE PICKUP AVAILABLE

Do not use fake urgency.

"Only 2 left" should only display when actual available stock is 2.

---

# 84. TRUST / CONVERSION FEATURES

Build original trust modules for:

- authentic products
- secure payment
- shipping
- returns
- support
- order tracking

These must correspond to real policies/settings.

Do not claim:

"100% authentic"

unless the merchant actually guarantees that.

Use configurable copy.

---

# 85. NEWSLETTER

Support:

- email capture
- consent checkbox where required
- double opt-in configuration
- campaign tags
- unsubscribe status

Prevent duplicate abuse.

Do not make newsletter popups immediately block the customer.

---

# 86. 404 / ROUTING

Create premium 404.

Examples:

"Sneaker not found"

with:

- search
- shop new arrivals
- shop popular products

Handle deleted/unpublished products gracefully.

---

# 87. FEATURE FLAGS

Provide a simple configuration mechanism for advanced modules:

ENABLE_REWARDS
ENABLE_GIFT_CARDS
ENABLE_STORE_PICKUP
ENABLE_RELEASE_DRAW
ENABLE_PRODUCT_COMPARE
ENABLE_PRICE_ALERTS
ENABLE_MPESA
ENABLE_REVIEWS

Disabled features must disappear cleanly from UI.

---

# 88. EXECUTION BEHAVIOR

You are expected to perform the work.

Do not stop after writing an architecture essay.

Do not ask me to manually create ordinary files you can create.

Do not ask for confirmation after every trivial phase.

Proceed autonomously through safe implementation steps.

Pause only when genuinely blocked by something requiring me, such as:

- production payment credentials
- external service account
- irreversible production operation
- ambiguous existing business decision
- missing proprietary product assets

Otherwise:

PLAN
IMPLEMENT
TEST
FIX
VERIFY
DOCUMENT

---

# 89. PROGRESS TRACKING

Create:

docs/BUILD_PROGRESS.md

Maintain:

## Completed

## In Progress

## Remaining

## Blocked

## Technical Decisions

Update it as work proceeds.

Do not mark items complete unless implemented.

---

# 90. FINAL REVIEW

At the end:

Use each relevant installed skill for one final review.

### Senior Architect
Architecture review

### UI/UX Pro Max
Visual/UX review

### Frontend Design
Interface quality review

### Senior Frontend
Frontend code review

### React Best Practices
Performance review

### Database Schema Designer
Schema/index review

### Senior Backend
API/business-rule review

### Security
Security review

### Senior QA
Test review

### Playwright
E2E review

### DevOps
Production-readiness review

Fix high/critical issues before finishing.

---

# 91. FINAL REPORT

At completion report:

## IMPLEMENTED

List major modules.

## DJANGO ADMIN

Explain everything now controllable from Admin.

## STOREFRONT

List completed pages.

## PRODUCT CARD

Confirm color-switch behavior.

## DATABASE

List major models/migrations.

## TESTING

Report:

Backend tests:
Frontend tests:
E2E tests:
Accessibility:
Production build:

Do not fabricate numbers.

## PERFORMANCE

Report actual checks performed.

## SECURITY

Summarize protections.

## RUN COMMANDS

Give exact local commands.

## ADMIN LOGIN

Explain how I create a development superuser.

Never embed a default production password.

## REMAINING EXTERNAL CONFIGURATION

Only list genuinely external items such as:

payment credentials
email provider
object storage
production domain

## IMPORTANT

If anything is incomplete:

say exactly what remains.

Do NOT say "perfect", "production-ready", or "100% complete" unless the
actual implementation and verification support that claim.

---

# ============================================================
# BEGIN NOW
# ============================================================

Start with:

1. repository inspection
2. installed skill inspection
3. Foot Locker UX/function audit if browsing is available
4. architecture plan
5. database design
6. design system
7. phased implementation
8. Django Admin
9. storefront
10. testing
11. security
12. final polish

The priority is:

FUNCTIONAL COMMERCE
        +
ADVANCED PREMIUM UI/UX
        +
DJANGO-ADMIN CONTROL
        +
RESPONSIVE DESIGN
        +
SECURITY
        +
PERFORMANCE
        +
TESTED PURCHASE FLOWS

Build the shoe store as a serious commercial platform, not a
demonstration template.