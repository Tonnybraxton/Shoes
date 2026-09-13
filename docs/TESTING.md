# Testing

Run backend commerce tests against PostgreSQL. They create and destroy a separate `test_soleline` database; the regular demonstration database is not reset. The PostgreSQL test role must be allowed to create a test database. Browser tests use the running demonstration store and leave synthetic accounts, carts and paid test orders in it. Never point them at production.

## Commands

Start the local database as described in README. From `backend`:

```powershell
$env:DEBUG='true'
$env:TEST_PAYMENTS='true'
$env:DATABASE_URL=(Get-Content ../.runtime/database-url -Raw).Trim()
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
.venv/Scripts/python.exe -m pytest -q --tb=short --basetemp=../.runtime/pytest-local
.venv/Scripts/python.exe -m pip_audit -r requirements.txt
```

The pytest temporary directory is dedicated to test output and can be cleared by pytest on the next run. Use a fresh directory if you need to preserve a failed run. Do not set `--basetemp` to a directory containing application or user data.

From `frontend`:

```powershell
npm run lint
npm run format:check
npm run typecheck
npm test
npm run build
npm audit --omit=dev --audit-level=high
```

With Django, PostgreSQL, a seeded catalogue and the frontend running:

```powershell
npm run test:e2e
# For a different isolated host:
$env:E2E_BASE_URL='http://localhost:8080'
npm run test:e2e
```

Playwright needs Chromium installed (`npx playwright install chromium`). On Windows, the runner and database helper need permission to spawn subprocesses. A sandbox `spawn EPERM` is a runner startup failure, not a passed or failed application assertion.

## Coverage and evidence

The backend suite covers published visibility, filters/search, exact SKU stock and repricing, CSRF, ownership, checkout/payment idempotency, provider retries, reservation expiry, final-unit contention and concurrent cart cleanup, promotions, reward deduplication, reviews, subscriptions, media validation and Admin inventory/role/CSV safeguards. Stripe calls are mocked; no live-provider charge is part of these tests.

Frontend unit tests cover variant image/link/price/availability updates, responsive rendition selection, safe links, money formatting, CMS settings, CSP media origin validation and the guest startup race under React StrictMode.

The 21 Chromium browser scenarios cover card swatches/expansion, PDP/size/cart, out-of-stock notification UI, combined URL filters, keyboard search, wishlist, comparison, guest simulated checkout, registration/profile/logout, releases, accessibility and nine viewport widths (320, 375, 390, 430, 768, 1024, 1280, 1440, 1920). The account scenario verifies that logout returns to sign-in, the server session is anonymous, and the edited profile survives a reload and a new sign-in. Axe scans home, catalogue, PDP, empty cart, account and releases with WCAG 2.0/2.1/2.2 A/AA tags. These scans do not replace screen-reader review or exhaustive manual keyboard testing.

The latest numerical results and remaining checks are recorded in BUILD_PROGRESS.md. Browser report: `frontend/playwright-report/index.html`; traces/screenshots for failures: `frontend/test-results`; selected storefront captures: `docs/screenshots`. Dependency audit JSON files are in ignored `.runtime` for the current workstation.

CI is configured to run backend/frontend checks and a full container/browser job on Linux. See the [GitHub Actions runs](https://github.com/Tonnybraxton/Shoes/actions) for remote results; the local results in BUILD_PROGRESS.md predate the initial GitHub upload. Local Docker build, nginx validation, Redis/Celery integration, HTTPS end-to-end checks, real Stripe sandbox webhooks and S3/SMTP integrations remain unverified.

## Local performance sample

With the production frontend build and local Django/PostgreSQL running, run `npm run measure:local` from `frontend`. Keep other tests and builds idle during this sample. The command uses the installed Chromium browser and only accepts a loopback `E2E_BASE_URL`.

It measures home, catalogue and product detail three times at each of two viewport sizes, using fresh browser contexts and a warmed server without CPU/network throttling. It observes navigation through initial images/fonts and another 1.5 seconds, recording TTFB, LCP and the largest CLS session window. The mobile-width sample changes viewport dimensions only; it does not emulate a phone's CPU or network. It also records 25 sequential response times for each of three public API endpoints through the frontend proxy after one warmup request per endpoint.

Raw results and the exact sampling method are saved to [local-performance.json](local-performance.json). The [performance report](PERFORMANCE.md) compares the initial sample with the loading-layout fix and records remaining latency gaps. This is a small workstation sample, not a load test or evidence of production Core Web Vitals. It does not measure INP, sustained concurrency, production caching or real mobile network behaviour.
