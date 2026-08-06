from django.contrib import admin

from .models import Membership, Team


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    fields = (
        "user",
        "role",
        "joined_at",
    )
    readonly_fields = ("joined_at",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_by",
        "member_count",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "created_by__username",
        "created_by__email",
    )

    list_filter = ("created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = ("created_by",)

    inlines = (MembershipInline,)

    @admin.display(description="Miembros")
    def member_count(self, obj):
        return obj.memberships.count()


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team",
        "user",
        "role",
        "joined_at",
    )

    search_fields = (
        "team__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "role",
        "joined_at",
    )

    readonly_fields = ("joined_at",)

    list_select_related = (
        "team",
        "user",
    )