# Build progress

Updated 2026-09-09. The master specification is broader than the current demonstration; no full-spec completion or launch certification is claimed.

## Completed

- Django/PostgreSQL commerce backend and Next.js storefront; 18 fictional shoes, 66 colourways and 660 size SKUs.
- Catalogue, URL filters/sorting, keyboard search, colourway cards, gallery/size selection, wishlist, comparison, cart, simulated checkout, orders, accounts/addresses, rewards accrual, verified-purchase review moderation and releases.
- Exact SKU inventory locks, expiring reservations, server repricing, promotions, payment/checkout idempotency and owner-scoped order access. Stripe provider calls are covered with mocks.
- Admin catalogue/variant/stock workflows, scheduled merchandising, navigation, policies, roles, CSV export and dry-run/atomic stock import.
- Validated uploads with retained originals and responsive WebP renditions. Fixed missing dimensions and connected renditions to cards and galleries.
- Fixed fresh-order decimal totals before Stripe minor-unit conversion. Synchronized dependency pins with configured Argon2 and S3 functionality.
- Fixed guest-cart startup races, serialized refreshes after mutations, and prevented a delayed profile load from replacing typed changes.
- Fixed password accessible labelling and homepage text contrast. Browser filter test now waits for sort navigation before reloading.
- Fixed logout retaining registration mode; successful logout clears account-page data and returns to sign-in, with errors reported and duplicate clicks disabled. Browser verification also checks anonymous server state and signing back in with persisted profile changes.
- Identified footer shifts during streamed loading and reserved the main content viewport; added a reproducible local browser/API performance sample with raw evidence.
- README and Admin, database, API, storefront, security, testing and deployment/recovery guides. Compose and GitHub Actions configuration present.

## Verification

| Check | Latest result |
| --- | --- |
| PostgreSQL backend suite | 72 passed |
| Frontend unit suite | 26 passed in 4 files |
| Django / production settings checks | Passed, no issues |
| Migration drift | No changes detected |
| Ruff lint / format | Passed |
| Frontend lint / format / TypeScript | Passed |
| Next.js production build | Passed, including logout and loading-layout fixes |
| Chromium browser suite | 21 passed; all 10 affected layout/accessibility scenarios passed again after the loading-layout fix |
| Accessibility | Zero axe violations on six sampled production-frontend routes; keyboard skip link passed |
| Responsive overflow | Passed at nine widths from 320 to 1920 px |
| Local performance sample | 18 page loads: median LCP 596–1124 ms; largest CLS 0.0147 after fix (initially 0.8851). API p95 63–390 ms; site/catalogue remain above the provisional 300 ms target. See PERFORMANCE.md |
| Dependency audits | Pinned Python and frontend production dependencies: no known vulnerabilities reported |
| Docker / remote CI / real providers | Not run here |

## Current status

The interrupted local integration verification is complete, including the account fix, production build, browser checks, refreshed screenshots and a measured loading-layout fix. Full-spec implementation and production validation remain incomplete as listed below. Raw performance samples and the repeatable command are documented in [PERFORMANCE.md](PERFORMANCE.md).

## Remaining implementation

- Automatic restock/release notifications and unsubscribe; newsletter currently records consent only.
- Authenticated storefront draft preview, VIDEO/DROP_COUNTDOWN CMS renderers, full advanced CMS controls and broader feature flags.
- Rewards redemption, provider refund execution and carrier fulfilment/tracking integration.
- Full quick view, video/360 viewer and complete international size-conversion merchandising.
- Manual screen-reader review, representative load/performance validation, SMTP/S3/Redis/Celery integration checks and a restore exercise.
- Site/catalogue API latency needs profiling and optimization before validating the provisional p95 target at realistic production load.
- Pickup, gift cards, raffles and M-Pesa remain unimplemented and unavailable.

These are implementation gaps, not merely missing credentials. Detailed limits are in STOREFRONT.md and ADMIN_GUIDE.md.

## Blocked external configuration and verification

- Docker is unavailable on this machine; container build/boot, nginx and HTTPS verification need a Docker-equipped host.
- The September 9 validation predates the initial GitHub upload. See [GitHub Actions](https://github.com/Tonnybraxton/Shoes/actions) for subsequent remote CI results.
- Payment credentials, verified SMTP, production storage/domain/TLS, merchant-approved policies, real assets/inventory, and monitoring/backup ownership have not been supplied.

## Technical decisions

- Django/PostgreSQL owns commerce transactions; same-origin sessions/CSRF, no browser-stored authentication token.
- Next.js 16/React 19 server-rendered discovery with client interaction components; installed framework docs take precedence over older examples.
- Public catalogue reads are currently uncached; Redis supports shared throttling/cache infrastructure and Celery.
- No fabricated customer reviews or default Admin credentials. Test accounts/orders are synthetic verification data.
- Targets, not guarantees: WCAG 2.2 AA, LCP <2.5 s, INP <200 ms, CLS <0.1, API p95 <300 ms at a defined load, availability 99.9%, RPO 24 h, RTO 4 h.
- Applied installed backend, frontend, QA and DevOps guidance to transaction correctness, responsive media, browser regressions and recovery documentation. No production deployment was attempted.
