from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "team",
        "created_by",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "team__name",
        "created_by__username",
        "created_by__email",
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "team",
        "created_by",
    )