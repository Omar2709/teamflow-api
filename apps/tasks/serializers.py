from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.teams.models import Membership

from .models import Task


User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.IntegerField(
        source="project_id",
        read_only=True,
    )

    created_by = serializers.SerializerMethodField()

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "created_by",
            "due_date",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project",
            "created_by",
            "created_at",
            "updated_at",
        )

    def get_created_by(self, task):
        if task.created_by is None:
            return None

        return {
            "id": task.created_by.id,
            "username": task.created_by.username,
            "email": task.created_by.email,
        }

    def validate_title(self, value):
        normalized_title = " ".join(value.split())

        if not normalized_title:
            raise serializers.ValidationError(
                "El título de la tarea no puede estar vacío."
            )

        return normalized_title

    def validate_assigned_to(self, user):
        if user is None:
            return None

        team = self.context.get("team")

        if team is None:
            return user

        if not Membership.objects.filter(
            team=team,
            user=user,
        ).exists():
            raise serializers.ValidationError(
                "El usuario asignado debe pertenecer al equipo."
            )

        return user