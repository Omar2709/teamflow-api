from django.conf import settings
from django.db import models
from django.db.models import Q


class Team(models.Model):
    name = models.CharField(
        max_length=120,
    )

    description = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_teams",
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="teams",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Propietario"
        ADMIN = "admin", "Administrador"
        MEMBER = "member", "Miembro"

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("joined_at",)

        constraints = [
            models.UniqueConstraint(
                fields=("team", "user"),
                name="unique_user_per_team",
            ),
            models.UniqueConstraint(
                fields=("team",),
                condition=Q(role="owner"),
                name="unique_owner_per_team",
            ),
        ]

        indexes = [
            models.Index(
                fields=("team", "role"),
                name="membership_team_role_idx",
            ),
            models.Index(
                fields=("user", "role"),
                name="membership_user_role_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.team.name} ({self.role})"
        )

MEMBERSHIP_ROLE_CHOICES = Membership.Role.choices

ASSIGNABLE_MEMBERSHIP_ROLE_CHOICES = (
    (
        Membership.Role.ADMIN,
        Membership.Role.ADMIN.label,
    ),
    (
        Membership.Role.MEMBER,
        Membership.Role.MEMBER.label,
    ),
)