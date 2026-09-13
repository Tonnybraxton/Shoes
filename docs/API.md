# API usage

The versioned JSON API is under `/api/v1/`; see [API_CONTRACT.md](API_CONTRACT.md) for endpoint payloads. Route implementation is in `backend/config/urls.py`, validation in `shop/serializers.py`, and transactional rules in `shop/services.py`.

Use the same origin as the storefront. Begin with `GET /api/v1/session/`, retain its cookies and send its returned `csrf_token` as `X-CSRFToken` on writes. Login rotates the CSRF token; use the token in the new session response. No bearer token is stored in the browser. Guest cart and signed guest order access are separate scopes.

List responses have `count`, `next`, `previous`, `results`, with pages of 24 records. Failures expose `error.code`, `error.message` and field details. Unpublished merchandise is absent from the public catalogue. Money values are decimal strings, inventory refers to the exact variant-size SKU, and timestamps include timezone information.

Checkout additionally requires an `Idempotency-Key` of up to 100 characters. Reuse it only for the same checkout payload, including retries after an ambiguous provider response. Real Stripe payments must arrive at `/api/v1/payments/stripe/webhook/` with a valid signature. The local `/payments/test/complete/` endpoint requires the checkout owner's session and is disabled outside explicit development mode.

Each product gallery image now includes `renditions: [{url,width,height}]` alongside its primary URL/dimensions. Clients should use width descriptors and `sizes` to select image files. Storage URLs are resolved when serializing, supporting local storage or the configured S3 backend.

`GET /api/v1/health/` checks PostgreSQL without disclosing credentials. API throttles are application-level safeguards; production needs shared Redis and perimeter request controls. The current subscription endpoints record consent but do not deliver restock/release alerts. Admin draft preview and automatic refund endpoints are not available.
