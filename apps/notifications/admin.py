from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "is_read",
        "task",
        "created_at",
    )

    search_fields = (
        "message",
        "user__username",
        "user__email",
        "task__title",
    )

    list_filter = (
        "type",
        "is_read",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "read_at",
    )

    list_select_related = (
        "user",
        "task",
    )