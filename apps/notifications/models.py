from django.conf import settings
from django.db import models

from apps.tasks.models import Task


class Notification(models.Model):
    class Type(models.TextChoices):
        TASK_ASSIGNED = (
            "task_assigned",
            "Tarea asignada",
        )
        TASK_DUE_SOON = (
            "task_due_soon",
            "Tarea próxima a vencer",
        )
        COMMENT_CREATED = (
            "comment_created",
            "Comentario creado",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
    )

    message = models.CharField(
        max_length=255,
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("user", "is_read"),
                name="notification_user_read_idx",
            ),
            models.Index(
                fields=("user", "created_at"),
                name="notification_user_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.message}"