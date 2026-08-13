from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "status",
        "priority",
        "assigned_to",
        "created_by",
        "due_date",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "project__name",
        "assigned_to__username",
        "assigned_to__email",
        "created_by__username",
    )

    list_filter = (
        "status",
        "priority",
        "due_date",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "project",
        "assigned_to",
        "created_by",
    )