# Storefront

Public pages use Next.js server rendering with uncached Django reads. Client components own search, filters, product selection, bag, checkout and account interactions. Global style tokens and responsive rules live in `frontend/src/app/globals.css`.

The current routes include home, all shoes, men/women/kids, sale, brands and brand detail, collections and collection detail, product detail, releases and release detail, wishlist, compare, recently viewed, cart, checkout, order confirmation, signed order tracking, account/profile/orders/addresses/rewards, email verification/password reset and help/policy pages. Unknown routes use the custom 404.

Filters and sorting are URL-backed. Product-card swatches retain layout dimensions while changing active variant, image, current price, availability and the product link. `+N` expands additional swatches. Gallery images use backend-generated responsive WebP sizes when available; legacy demo assets use their original URL. Native lazy loading applies to cards and priority loading to the main product image.

Guest bag ownership uses a server session cookie. Startup establishes one bag before an add can execute, including development StrictMode. Later session refreshes are serialized so profile changes fetch current state. Guest wishlist storage contains product IDs; signed-in accounts merge them with the backend. Comparison uses session storage and supports four products. Recently viewed history and analytics require the optional consent choice.

The profile form waits for the current customer's details before allowing edits. Successful logout clears account-page data and returns to sign-in; failures show a notification and allow retry. The main region reserves at least one viewport of height so the footer does not jump out of the first screen as route content streams in.

Checkout requires an exact size SKU and uses server totals. The local test payment path is visibly labelled and requires explicit development settings. Stripe redirects to hosted checkout; the browser does not decide whether an order is paid. Account/order/return endpoints enforce ownership. Shipping currently supports standard delivery in Kenya.

## Current scope limits

This is a working demonstration, not a launch certification. There is no automatic restock/release email delivery, unsubscribe workflow, rewards redemption, provider refund execution, carrier booking/tracking integration, full CMS draft storefront preview, video/360 viewer or complete set of advanced homepage renderers. Product comparison and review display are present, but not every module has a merchant-controlled feature flag. Pickup, raffles and gift cards remain disabled.

The public rewards page describes accrual and the account ledger; business rewards terms/redemption still need implementation. The fit helper is illustrative, not a measured fit guarantee. All seeded brands, shoes and specifications are fictional. Replace them and review every visible claim before accepting real orders.

The desktop and mobile screenshots in `docs/screenshots` are local test artifacts. Accessibility checks cover sampled routes and interactions; automated axe results alone do not establish complete WCAG conformance.
