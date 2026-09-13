# SOLELINE API contract

Working contract, v1. Django owns all business data. Next.js uses same-origin `/api/v1/` (rewrite locally, reverse proxy in production). Decimal monetary values are JSON strings; KES is the initial configured currency. IDs are numbers except opaque cart/order references. Timestamps are ISO8601. Media URLs are absolute or `/media/...`.

## Common

Error: `{ "error": { "code": "validation_error", "message": "...", "fields": {} } }`. Lists: `{ "count": 30, "next": "url or null", "previous": null, "results": [] }`. Public lists paginate. Mutations require session CSRF; `GET /session/` returns `{user: null | {id,email,first_name}, csrf_token: "..."}` and sets cookies. HttpOnly session auth. Guest cart associated with session; authenticated ownership enforced.

## Catalog

`GET /site/` returns `{name, tagline, currency, announcements:[{id,text,href}], navigation:[{label,href,children:[]}], sections:[{id,type,title,subtitle,body,image,href,cta,settings:{},products:[]}], flags:{pickup:false,raffles:false,gift_cards:false}, payment_enabled:false, demo:true, footer:[]}`. Only active/scheduled content and published products public. Staff preview token is a separate permissioned pathway. Homepage seed provides HERO, PRODUCT_CAROUSEL, CATEGORY_GRID, EDITORIAL_SPLIT, BRAND_GRID, NEWSLETTER, TRUST_BAR.

`GET /products/?search=&gender=&brand=&category=&collection=&size=&color=&min_price=&max_price=&sale=true&in_stock=true&sort=featured&page=1`. Support additional filters when data exists (sport,style,new,best,limited,rating,age,promo_eligible,free_shipping). `sort`: featured,newest,bestselling,rating,price_asc,price_desc,name. Multiple filter values comma separated. `GET /facets/` returns `{brands:[{slug,name,count}],categories:[{slug,name,count}],sizes:[{id,label,system,count}],colors:[{name,code,count}],genders:[{value,label,count}],price:{min,max}}` calculated from published inventory; contextual counts where feasible.

Product response used both cards and details:

```json
{"id":1,"slug":"velocity-02","name":"Velocity 02","subtitle":"Everyday running shoes","description":"...","brand":{"id":1,"name":"ARC","slug":"arc","logo":""},"category":{"id":1,"name":"Running","slug":"running"},"gender":"unisex","age_group":"adult","sport":"running","style":"performance","price":"12900.00","compare_at_price":null,"rating":null,"review_count":0,"is_new":true,"is_featured":true,"is_best_seller":false,"is_limited":false,"badges":["New arrival"],"default_variant_id":1,"max_card_swatches":4,"fit":"true","width":"regular","details":["Mesh upper","Rubber outsole"],"variants":[{"id":1,"sku":"ARC-V02-OLIVE","color_name":"Olive / Chalk","color_code":"#82866d","color_family":"green","price":"12900.00","compare_at_price":null,"is_default":true,"in_stock":true,"image":"/media/demo/olive.webp","hover_image":"/media/demo/olive-detail.webp","images":[{"id":1,"url":"/media/demo/olive.webp","alt":"DEMO olive shoe lateral view","view_type":"PRIMARY","width":1000,"height":800}],"sizes":[{"id":1,"size_id":1,"label":"41","system":"EU","sku":"ARC-V02-OLIVE-41","available":6}]}],"seo_title":"...","seo_description":"..."}
```

`GET /products/{slug}/` same plus complete gallery/specifications, published only. `GET /products/{slug}/related/` list envelope. `GET /products/{slug}/reviews/` approved verified reviews envelope. `POST` authenticated verified buyer `{rating,title,body,fit,comfort}` -> pending moderation. No demo fake ratings. `GET /search/?q=...` -> `{products:[product],brands:[],categories:[],suggestions:[]}` bounded autocomplete.

`GET /brands/` and `/collections/` list envelopes of `{id,name,slug,description,image}`. `GET /releases/?status=upcoming|released&brand=&month=` list envelope of `{id,title,slug,release_at,status,image,product:product|null,description}`; `GET /releases/{slug}/` detail. `GET /stores/` only enabled stores; no fabricated pickup.

## Commerce

`GET /cart/`: `{id,items:[{id,quantity,variant_size_id,product_slug,product_name,brand,color_name,size_label,image,unit_price,line_total,available}],subtotal,discount,shipping,total,currency,promo_code,free_shipping_remaining}`. Server evaluates current prices and inventory. `POST /cart/items/` `{variant_size_id,quantity}`; `PATCH /cart/items/{id}/` `{quantity}`; `DELETE` same. All return full cart. `POST /cart/promo/` `{code}` full cart. `DELETE /cart/promo/` clears.

`POST /checkout/` with `Idempotency-Key` header; body `{email,first_name,last_name,phone,address:{line1,line2,city,county,postal_code,country:"KE"},shipping_method:"standard",payment_provider:"stripe"|"test",consent:true}`. Server creates immutable pending order under locks, reserves stock, creates provider session, never trusts prices. Return `{order:{reference,status,total,currency,tracking_token},payment:{provider,redirect_url,client_secret},test_mode:false}`. No real credentials => safe payment unavailable response. Test provider permitted only explicit development/testing server setting, with UI clear and no production success claims. Webhook verifies signatures, event ID/amount/currency and paid state before fulfillment. Test completion endpoint only if nonproduction + explicit test provider setting: `POST /payments/test/complete/` `{reference}` -> verified local simulated payment order (for automated E2E).

`GET /orders/` owned orders list. `GET /orders/{reference}/` owned or signed guest `?token=` returns `{reference,status,email,created_at,items:[...],subtotal,discount,shipping,total,currency,address,history:[]}`. `POST /tracking/` `{reference,token}` same; no guessable email+order tracking. `POST /returns/` `{order_reference,items:[{order_item_id,quantity}],reason,request_type:"refund"}` authenticated eligible order owner. No automatic refund until provider-confirmed operation.

## Accounts and engagement

`POST /auth/register/` `{email,password,first_name,last_name}`; `POST /auth/login/` `{email,password}` returns session; `POST /auth/logout/`. `POST /auth/password-reset/` `{email}` generic response; `POST /auth/password-reset/confirm/` `{uid,token,password}`. `POST /auth/verify/` `{uid,token}`. `GET|PATCH /account/` profile `{email,first_name,last_name,phone,usual_size,size_system,fit_preference}`. `GET|POST /addresses/` and `PATCH|DELETE /addresses/{id}/` scoped to account.

`GET /wishlist/` -> `{products:[]}`; `POST /wishlist/` `{product_id}`; `DELETE /wishlist/{product_id}/`; `POST /wishlist/merge/` `{product_ids:[]}`. Guest localStorage only non-sensitive IDs; merge on authentication. `GET /rewards/` -> `{name,points,tier,ledger:[],enabled:true}` for authenticated; anonymous description. `POST /restock-alerts/` `{variant_size_id,email,consent:true}`; `POST /release-alerts/` `{release_id,email,consent:true}`. `POST /newsletter/` `{email,consent:true}`. `POST /analytics/` event allowlist, consent required, no PII payload accepted. `GET /policies/{slug}/` admin content `{title,body,updated_at}`.

## Admin and operations

Django Admin `/admin/`. Role groups are scoped by actual model permissions. Admin edits and catalogue export require staff access. Inventory import is a validated CLI command, with a dry run by default. An authenticated storefront draft preview is not implemented. Health `/api/v1/health/` exposes no secrets. PostgreSQL is required except for the explicit development SQLite option; SQLite cannot establish row-lock guarantees. Money, stock, redemption and order transition invariants are verified using PostgreSQL tests. Subscription endpoints currently record consent only; automatic alert delivery and unsubscribe handling remain unimplemented.
