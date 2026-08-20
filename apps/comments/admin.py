from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "author",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "content",
        "task__title",
        "author__username",
        "author__email",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "task",
        "author",
    )