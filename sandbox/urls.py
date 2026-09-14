from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import admin
from django.conf import settings
from strawberry.django.views import AsyncGraphQLView
from .schema import public_schema, dashboard_schema
from utils.views import home


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path(
        "graphql/",
        ensure_csrf_cookie(AsyncGraphQLView.as_view(schema=public_schema)),
        name="graphql-api",
    ),
    path(
        "dashboard/graphql/",
        ensure_csrf_cookie(AsyncGraphQLView.as_view(schema=dashboard_schema)),
        name="dashboard-graphql-api",
    ),
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
