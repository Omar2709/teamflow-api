from rest_framework import serializers

from .models import (
    ASSIGNABLE_MEMBERSHIP_ROLE_CHOICES,
    Membership,
    Team,
)
from drf_spectacular.utils import extend_schema_field

from apps.users.serializers import UserSummarySerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class TeamSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "member_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_by",
            "member_count",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(
        UserSummarySerializer(
            allow_null=True,
        )
    )

    def get_created_by(self, team):
        if team.created_by is None:
            return None

        return {
            "id": team.created_by.id,
            "username": team.created_by.username,
            "email": team.created_by.email,
        }

    def get_member_count(self, team) -> int:
        annotated_count = getattr(
            team, 
            "member_count",
            None
        )

        if annotated_count is not None:
            return annotated_count
        return team.memberships.count()
    


    def validate_name(self, value):
        normalized_name = " ".join(value.split())

        if not normalized_name:
            raise serializers.ValidationError(
                "El nombre del equipo no puede estar vacío."
            )

        return normalized_name

class TeamMembershipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Membership
        fields = (
            "id",
            "username",
            "email",
            "role",
            "joined_at",
        )
        read_only_fields = fields

class TeamMembershipCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    role = serializers.ChoiceField(
        choices=ASSIGNABLE_MEMBERSHIP_ROLE_CHOICES,
        
        default=Membership.Role.MEMBER,
    )

    def validate(self, attrs):
        username = attrs["username"]
        team = self.context["team"]

        user = User.objects.filter(
            username=username,
        ).first()

        if user is None:
            raise serializers.ValidationError(
                {
                    "username": (
                        "No existe un usuario con ese nombre."
                    )
                }
            )

        if Membership.objects.filter(
            team=team,
            user=user,
        ).exists():
            raise serializers.ValidationError(
                {
                    "username": (
                        "Este usuario ya pertenece al equipo."
                    )
                }
            )

        attrs["user"] = user

        return attrs

class TeamMembershipRoleUpdateSerializer(
    serializers.ModelSerializer
):
    role = serializers.ChoiceField(
        choices=ASSIGNABLE_MEMBERSHIP_ROLE_CHOICES
    )
    class Meta:
        model = Membership
        fields = ("role",)

class TeamOwnershipTransferSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        min_value=1,
    )

class DashboardTaskBreakdownSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
    todo = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    done = serializers.IntegerField(read_only=True)


class DashboardProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    tasks = DashboardTaskBreakdownSerializer(
        read_only=True,
    )


class DashboardProjectsSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
    breakdown = DashboardProjectSerializer(
        many=True,
        read_only=True,
    )


class DashboardTeamSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    members = serializers.IntegerField(read_only=True)


class DashboardTaskMetricsSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
    todo = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    done = serializers.IntegerField(read_only=True)
    overdue = serializers.IntegerField(read_only=True)
    due_soon = serializers.IntegerField(read_only=True)
    unassigned = serializers.IntegerField(read_only=True)
    low = serializers.IntegerField(read_only=True)
    medium = serializers.IntegerField(read_only=True)
    high = serializers.IntegerField(read_only=True)


class DashboardMyTaskMetricsSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
    todo = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    done = serializers.IntegerField(read_only=True)
    overdue = serializers.IntegerField(read_only=True)
    due_soon = serializers.IntegerField(read_only=True)


class TeamDashboardResponseSerializer(serializers.Serializer):
    team = DashboardTeamSerializer(read_only=True)
    projects = DashboardProjectsSerializer(read_only=True)
    tasks = DashboardTaskMetricsSerializer(read_only=True)
    my_tasks = DashboardMyTaskMetricsSerializer(
        read_only=True,
    )