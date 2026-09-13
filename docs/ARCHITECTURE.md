# Architecture

SOLELINE is a modular monolith with one transactional commerce authority: Django/PostgreSQL. Next.js renders public discovery on the server and small client components handle variant selection, filters, wishlist, cart and checkout. The public API contract is in API_CONTRACT.md.

Backend services cover catalog and stock, merchandising, customers, orders/payments/promotions, and engagement. Foreign keys, database constraints and atomic services enforce boundaries; the storefront never computes authoritative order totals. Public catalogue projections currently read from PostgreSQL without a response cache. Redis supports shared throttling/cache infrastructure and Celery. Outbox records decouple transactional events from email delivery. Public reads reflect Admin publication changes directly.

Production is a same-origin reverse proxy with frontend, backend, worker, PostgreSQL and Redis. No cross-origin authentication token architecture is needed. Development proxies API and media from Next.js. Uploaded media must be validated and non-executable; production media belongs on a distinct origin/object store. Settings fail closed for secret keys, test payments and insecure cookies in production.

## Decisions

- ADR-001: modular monolith chosen for small team operation and database transactions over premature distributed services.
- ADR-002: Django 5.2 LTS supports existing Python 3.10; update patches via dependency review. Next/React use compatible stable releases verified at initialization.
- ADR-003: opaque UUID public orders plus signed guest access, HttpOnly sessions and CSRF protect identity and ownership.
- ADR-004: inventory locks, expiring reservations, idempotency keys and verified payment webhooks prevent duplicate fulfillment. Reprice before reservation and check exact size SKU.
- ADR-005: explicit sandbox configuration; absent payment credentials disable real checkout. A local test provider exists only for automated/development validation and must never be accepted in production.
- ADR-006: structured scheduled CMS blocks avoid arbitrary HTML execution. Feature flags hide optional unimplemented flows.
- ADR-007: original editorial design and generated demonstration merchandise avoid reliance on third-party trademarks/assets.

The deployment guide must state the operator responsibilities and the evidence still required before public launch. Targets recorded in BUILD_PROGRESS.md are provisional acceptance goals, not measured service guarantees.
