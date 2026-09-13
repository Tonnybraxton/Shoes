# Security and operating boundaries

The current controls include server-side Django sessions, HttpOnly/SameSite cookies, CSRF on writes including anonymous checkout, Argon2 password hashing, password validation/reset tokens, signed guest order access, owner-scoped reads/writes and Django staff permissions. Production settings require a strong secret, secure cookies, HTTPS and disabled test payments.

Commerce totals are server-authoritative. PostgreSQL locks and database constraints protect reservations, final-unit contention, promotion limits and order/payment idempotency. Stripe signatures, amount, currency and session are checked before stock consumption. Expired or incomplete reservations require operator reconciliation; they cannot produce fulfilment success. No raw card details are collected by this application.

The storefront applies a per-request nonce Content Security Policy, disallows frames/objects and limits payment redirects to Stripe's HTTPS checkout host. Optional media origin configuration only accepts a single HTTPS origin. Structured CMS copy is rendered as text; local links are validated. Uploads are bounded, decoded and re-encoded as WebP. Validated originals are retained, including original metadata; grant access and retention accordingly. Generated demonstration SVG files are trusted application assets, not an accepted upload format.

Inventory Admin rechecks current reservations under a lock. Financial/inventory ledgers cannot be created/deleted manually through their Admin interfaces. Catalogue CSV export escapes spreadsheet formula prefixes. Request logs contain IDs, method, path, status and duration, rather than credentials or request bodies. Guest tracking tokens must not be copied into support messages or analytics.

## Before launch

- Configure HTTPS, actual allowed hosts/CSRF origin, shared Redis, verified payment webhooks, SMTP and isolated media storage. Keep application/database ports private.
- Review least-privilege operator roles, enable staff MFA through the chosen identity/access solution, and establish credential rotation and incident response ownership. MFA is not built into this project's current login.
- Replace demo merchandise and policy text. Define retention/deletion procedures for customer data, uploads, subscriptions, backups and logs.
- Validate real-provider success/failure/refund/reconciliation paths and notification delivery. Automated unsubscribe, marketing delivery and provider refunds remain implementation gaps.
- Run the dependency audits and CI gates, a staging penetration/security review and an actual backup restore exercise.

No real credentials are stored in tracked example files. `.runtime`, `.env`, media and local database content are ignored. Deployment remains unverified on this workstation because Docker is unavailable; passing Django security checks is not a substitute for testing the complete HTTPS stack.
