from django.conf import settings
from django.db import models

from apps.projects.models import Project


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "Pendiente"
        IN_PROGRESS = "in_progress", "En progreso"
        DONE = "done", "Completada"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(
        max_length=160,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("project", "status"),
                name="task_project_status_idx",
            ),
            models.Index(
                fields=("project", "priority"),
                name="task_project_priority_idx",
            ),
            models.Index(
                fields=("assigned_to", "status"),
                name="task_assignee_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.title}"