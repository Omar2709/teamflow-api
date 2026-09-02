from django.contrib import admin
from django.urls import include, path
from config.health import health, readiness
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/auth/",
        include("apps.users.urls"),
    ),

    path(
        "api/",
        include("apps.teams.urls"),
    ),
    path(
        "api/",
        include("apps.projects.urls"),
    ),
    path(
        "api/",
        include("apps.tasks.urls"),
    ),
    path(
        "api/",
        include("apps.comments.urls"),
    ),
    path(
        "api/",
        include("apps.notifications.urls"),
    ),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="redoc",
    ),
    path(
        "health/",
        health,
        name="health",
    ),
    path(
        "ready/",
        readiness,
        name="readiness",
    ),
]