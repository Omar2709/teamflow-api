from django.conf import settings
from django.db import models

from apps.tasks.models import Task


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="task_comments",
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(
                fields=("task", "created_at"),
                name="comment_task_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.task.title} - {self.author}"