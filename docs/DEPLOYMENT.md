# Deployment and recovery

The supplied Compose stack has nginx, Next.js, Django/Gunicorn, PostgreSQL, Redis, a Celery worker, one beat scheduler and a one-off migration/static-file init service. The production overlay enables Django HTTPS settings and mounts TLS certificates. Application containers run as an unprivileged user. This stack has not been built or booted on the current Windows host: Docker is unavailable. CI contains the build/start/health/browser gates for a Docker-equipped Linux runner.

## Staging first

1. Copy `.env.example` to an ignored environment file and replace both secrets independently. Supply the actual public origin, allowed host, CSRF origin, SMTP configuration and TLS certificate directory. Use separate staging and production databases, buckets and payment credentials.
2. Inspect `docker compose -f compose.yaml -f infrastructure/compose.production.yaml config --quiet`. Avoid printing the resolved configuration in shared logs because it includes secrets.
3. Build on a trusted runner and tag immutable images using `BACKEND_IMAGE`/`FRONTEND_IMAGE`. `NEXT_PUBLIC_SITE_URL` and API rewrite settings are set during the frontend build. Rebuild when these values change.
4. Back up the database and media; then start the reviewed stack using `docker compose -f compose.yaml -f infrastructure/compose.production.yaml up --build --detach --wait`. The init service migrates, creates missing role groups and collects static assets before the app starts.
5. Run `docker compose exec backend python manage.py check --deploy --fail-level WARNING`, `docker compose exec proxy nginx -t`, health/API/Admin/media checks and real staging browser/payment/SMTP checks. Create the first superuser interactively. Never run demo seeding in production.

The proxy binds to loopback by default. Set `PROXY_BIND_IP` deliberately on the deployment host. The base HTTP port remains present with the production overlay and redirects to HTTPS. PostgreSQL's host mapping is loopback-only; omit it when host access is unnecessary. Never expose the Django container directly when `TRUST_PROXY=true`; nginx must overwrite forwarding headers. Configure firewall and certificate renewal for the chosen host.

## Media and payments

Set `USE_S3=true`, bucket, region/endpoint and credentials or an instance role for production object storage. Use a dedicated read-only HTTPS media hostname, `AWS_S3_CUSTOM_DOMAIN`, and the matching `MEDIA_ORIGIN` for the frontend CSP. Configure bucket access/CDN policy and retention externally. With signed URLs, account for their expiry in caches. Local volume media remains available for development. Old replaced uploads are retained until an operator-defined cleanup process removes unreferenced objects.

Set Stripe secret/webhook values and register the webhook endpoint at `/api/v1/payments/stripe/webhook/`. Verify sandbox payments, retries, duplicate events and delayed/expired reservations before live mode. The test provider is refused by production settings. M-Pesa, carrier integration and programmatic refunds are not implemented; do not enable them through UI claims.

## Backups and restoration

Use PostgreSQL `pg_dump --format=custom` from a trusted backup job, storing encrypted output outside the application host. Snapshot/version the media bucket or persistent media volume as well. Target daily backups (provisional RPO 24 hours), retain multiple generations, and alert on failed/old backups. The recovery target is four hours pending a timed restore drill.

Restore into a **new isolated database** with `pg_restore --no-owner --no-acl --dbname=<new-database> <backup-file>`. Supply credentials through the deployment secret mechanism, not shell history. Restore matching media, point an isolated app at the restored services, run migration/status checks and verify catalogue, orders, reservations and sample files before switching traffic. No restore or destructive database replacement was performed during this build.

## Rollback and monitoring

Keep the prior immutable application image tags. On an application failure, restore those tags only after confirming schema compatibility; an incompatible migration needs its reviewed reverse/data-recovery plan. Do not automatically reverse migrations or run `down --volumes` on a persistent environment. Disable checkout during payment or stock inconsistencies and reconcile pending provider events before resuming.

Monitor health and latency, HTTP error rate, worker/beat availability, unsent Outbox rows (especially `attempts >= 10`), aged pending orders, reservation totals, PostgreSQL connections/disk, Redis health, TLS expiry and backup age. Keep one beat scheduler. A crash after SMTP acceptance but before database commit can duplicate an email; provider-level idempotency is not implemented. No hosted monitoring service, uptime guarantee or verified restore time is claimed.
