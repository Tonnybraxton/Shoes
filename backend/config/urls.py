from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from shop import api

admin.site.site_header = "SOLELINE Commerce"
admin.site.site_title = "SOLELINE Admin"
admin.site.index_title = "Manage your storefront"
urlpatterns = [path("admin/", admin.site.urls)]
routes = [
    ("health/", api.health, {}),
    ("session/", api.session, {}),
    ("site/", api.site, {}),
    ("products/", api.products, {}),
    ("products/<slug:slug>/", api.products, {}),
    ("products/<slug:slug>/related/", api.related, {}),
    ("products/<slug:slug>/reviews/", api.reviews, {}),
    ("facets/", api.facets, {}),
    ("search/", api.search, {}),
    ("brands/", api.directory, {"kind": "brands"}),
    ("collections/", api.directory, {"kind": "collections"}),
    ("stores/", api.directory, {"kind": "stores"}),
    ("releases/", api.releases, {}),
    ("releases/<slug:slug>/", api.releases, {}),
    ("cart/", api.cart, {}),
    ("cart/items/", api.cart, {}),
    ("cart/items/<int:item_id>/", api.cart, {}),
    ("cart/promo/", api.cart, {"action": "promo"}),
    ("checkout/", api.checkout, {}),
    ("payments/test/complete/", api.test_complete, {}),
    ("payments/stripe/webhook/", api.stripe_webhook, {}),
    ("orders/", api.orders, {}),
    ("orders/<uuid:reference>/", api.orders, {}),
    ("tracking/", api.orders, {}),
    ("auth/password-reset/confirm/", api.auth, {"action": "password-reset-confirm"}),
    ("auth/<slug:action>/", api.auth, {}),
    ("account/", api.account, {}),
    ("addresses/", api.addresses, {}),
    ("addresses/<int:pk>/", api.addresses, {}),
    ("wishlist/", api.wishlist, {}),
    ("wishlist/merge/", api.wishlist, {"merge": True}),
    ("wishlist/<int:product_id>/", api.wishlist, {}),
    ("rewards/", api.rewards, {}),
    ("returns/", api.returns, {}),
    ("restock-alerts/", api.subscribe, {"kind": "restock"}),
    ("release-alerts/", api.subscribe, {"kind": "release"}),
    ("newsletter/", api.subscribe, {"kind": "newsletter"}),
    ("analytics/", api.analytics, {}),
    ("policies/<slug:slug>/", api.policy, {}),
]
urlpatterns += [path("api/v1/" + route, view, kwargs) for route, view, kwargs in routes]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
