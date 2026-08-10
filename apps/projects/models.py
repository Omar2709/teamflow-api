from django.conf import settings
from django.db import models

from apps.teams.models import Team


class Project(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="projects",
    )

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
        related_name="created_projects",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("team", "name"),
                name="unique_project_name_per_team",
            ),
        ]

    def __str__(self):
        return f"{self.team.name} - {self.name}"