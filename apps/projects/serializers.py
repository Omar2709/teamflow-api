from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.users.serializers import UserSummarySerializer
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField(
        source="team_id",
        read_only=True,
    )

    created_by = serializers.SerializerMethodField()

    class Meta:           # pyright: ignore[reportIncompatibleVariableOverride]
        model = Project
        fields = (
            "id",
            "team",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "team",
            "created_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(
        UserSummarySerializer(
         allow_null=True,
        )
    )

    def get_created_by(self, project):
        if project.created_by is None:
            return None

        return {
            "id": project.created_by.id,
            "username": project.created_by.username,
            "email": project.created_by.email,
        }

    def validate_name(self, value):
        normalized_name = " ".join(value.split())

        if not normalized_name:
            raise serializers.ValidationError(
                "El nombre del proyecto no puede estar vacío."
            )

        team = self.context.get("team")

        if team is not None:
            queryset = Project.objects.filter(
                team=team,
                name=normalized_name,
            )

            if self.instance is not None:
                queryset = queryset.exclude(
                    pk=self.instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe un proyecto con este nombre "
                    "en el equipo."
                )

        return normalized_name