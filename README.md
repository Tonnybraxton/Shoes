# SOLELINE

A shoe commerce demonstration built with Next.js, React, Django and PostgreSQL. The catalogue, colourways, size stock, carts, orders, accounts and merchandising are backed by Django. Prices use KES; the initial delivery region is Kenya.

**This is a development store with fictional merchandise.** Real payments, fulfilment, legal policies and production infrastructure need operator configuration and validation. See [build status](docs/BUILD_PROGRESS.md) for verified results and implementation limits.

## Screenshots

Desktop and mobile captures of the locally running demonstration store. Browse the [full screenshot gallery](docs/screenshots/README.md) for larger images and the shopping flow.

![SOLELINE desktop storefront with shoe hero and new arrivals](docs/screenshots/storefront-preview.png)

| Catalogue | Product detail |
| --- | --- |
| ![Shoe catalogue with filters and colourways](docs/screenshots/catalog-desktop.png) | ![Velocity 02 product gallery and size selection](docs/screenshots/product-desktop.png) |

| Shopping bag | Demonstration checkout |
| --- | --- |
| ![Shopping bag with selected size and order summary](docs/screenshots/cart-desktop.png) | ![Checkout with delivery details and demonstration payment](docs/screenshots/checkout-desktop.png) |

<p align="center">
  <img src="docs/screenshots/mobile-preview.png" alt="SOLELINE mobile storefront at 390 pixels wide" width="300" />
</p>

## Features

- Responsive storefront with search, catalogue filters, sorting and colourway selection.
- Product galleries, size availability, wishlist, comparison and a server-priced shopping bag.
- Simulated checkout, customer accounts, order history and delivery addresses.
- Django Admin for products, stock, merchandising and staff roles.
- PostgreSQL-backed inventory reservations, checkout idempotency and owner-scoped orders.
- Docker Compose configuration, automated tests and a GitHub Actions workflow.

## Local development on Windows

Prerequisites: Node.js 24, Python 3.10–3.12, npm, and PowerShell. Clone the repository and enter its folder first:

```powershell
git clone https://github.com/Tonnybraxton/Shoes.git
Set-Location Shoes
```

Commands below start from the project root unless stated otherwise. Install the dependencies for a fresh checkout:

```powershell
npm ci
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

Start the bundled, persistent development PostgreSQL server in one terminal:

```powershell
npm run db
```

It binds to `127.0.0.1:55432`, stores its data in `.runtime/postgres`, and writes its generated connection URL to `.runtime/database-url`. Keep this terminal running. Ctrl+C stops the server without deleting data. Do not share the ignored connection file or database folder. To use an existing PostgreSQL database, set `DATABASE_URL` instead.

In a second terminal:

```powershell
Set-Location backend
$env:DEBUG='true'
$env:TEST_PAYMENTS='true'
$env:DATABASE_URL=(Get-Content ../.runtime/database-url -Raw).Trim()
$env:SITE_URL='http://127.0.0.1:3000'
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py setup_roles
.venv/Scripts/python.exe manage.py seed_demo
.venv/Scripts/python.exe manage.py collectstatic --noinput
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000
```

In a third terminal:

```powershell
Set-Location frontend
npm run dev
```

Open [the store](http://127.0.0.1:3000) and [Django Admin](http://127.0.0.1:8000/admin/). Use the same host spelling throughout your browser session. The frontend proxies `/api/` and `/media/` to Django. `TEST_PAYMENTS=true` enables clearly labelled simulated checkout; no charge is made. Leave it false to test the unavailable-payment state.

Create your own Admin account from another backend terminal with the same environment:

```powershell
.venv/Scripts/python.exe manage.py createsuperuser
```

No default username or password is shipped. `setup_roles` creates staff groups, preserves existing permissions, and creates no users. `seed_demo` preserves existing merchant records and refuses to run with production settings or S3 storage.

## Background work

For a complete local stack with Redis, Celery, nginx and both applications, use Docker Compose. Copy `.env.example` to `.env`, replace its example secrets, and then run:

```powershell
docker compose up --build --detach --wait
docker compose exec backend python manage.py seed_demo
docker compose exec backend python manage.py createsuperuser
```

Open [the container store](http://localhost:8080) and [container Admin](http://localhost:8080/admin/). Stop services using `docker compose down`; omit `--volumes` to retain data. Docker is not installed on the development machine used for the September 9 validation.

Without Compose, set `REDIS_URL` to a running Redis instance in each backend process, then run a worker and one scheduler in separate terminals:

```powershell
.venv/Scripts/python.exe -m celery -A config worker --loglevel=info --pool=solo
.venv/Scripts/python.exe -m celery -A config beat --loglevel=info
```

The solo pool is for Windows development. Containers use the normal Linux worker pool. No Redis means a process-local memory transport; separate workers cannot communicate through it. For a one-off local check, `manage.py shell -c "from shop.tasks import expire_reservations; expire_reservations()"` releases expired reservations. The analogous `deliver_outbox()` call sends queued emails through the configured backend; DEBUG defaults to console output.

## Verification and operations

- [Testing and exact commands](docs/TESTING.md)
- [Local performance measurements](docs/PERFORMANCE.md)
- [Admin guide](docs/ADMIN_GUIDE.md)
- [Storefront behaviour and limits](docs/STOREFRONT.md)
- [Architecture](docs/ARCHITECTURE.md) and [database](docs/DATABASE.md)
- [API](docs/API.md) and [request/response contract](docs/API_CONTRACT.md)
- [Security](docs/SECURITY.md) and [deployment, backup and rollback](docs/DEPLOYMENT.md)

`requirements.in` lists direct backend constraints; `requirements.txt` pins the tested environment, including transitive dependencies. Refresh pins deliberately in a clean environment and rerun audits and tests. Frontend versions are locked by `frontend/package-lock.json`. `.env` is read by Compose; Django does not automatically load that file when run directly.
