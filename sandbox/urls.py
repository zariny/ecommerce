from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from strawberry.django.views import AsyncGraphQLView
from .schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", AsyncGraphQLView.as_view(schema=schema)),
    # path("api/", include("products.urls")),
    # path("api/", include("catalogue.urls")),
    # path("api/", include("account.urls")),
    # path("api/", include("order.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
