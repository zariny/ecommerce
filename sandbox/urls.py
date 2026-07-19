from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from strawberry.django.views import AsyncGraphQLView
from .schema import public_schema, dashboard_schema


urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", AsyncGraphQLView.as_view(schema=public_schema)),
    path("dashboard/graphql/", AsyncGraphQLView.as_view(schema=dashboard_schema)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
