from django.contrib import admin
from django.urls import include, path


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
]