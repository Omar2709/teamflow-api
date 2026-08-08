from rest_framework import serializers

from .models import Membership,Team

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

    def get_created_by(self, team):
        if team.created_by is None:
            return None

        return {
            "id": team.created_by.id,
            "username": team.created_by.username,
            "email": team.created_by.email,
        }

    def get_member_count(self, team):
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
        choices=(
            (
                Membership.Role.ADMIN,
                "Administrador",
            ),
            (
                Membership.Role.MEMBER,
                "Miembro",
            ),
        ),
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
        choices=(
            (
                Membership.Role.ADMIN,
                "Administrador",
            ),
            (
                Membership.Role.MEMBER,
                "Miembro",
            ),
        )
    )

    class Meta:
        model = Membership
        fields = ("role",)

class TeamOwnershipTransferSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        min_value=1,
    )