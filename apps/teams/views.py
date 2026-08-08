from django.db import transaction
from django.db.models import Count
from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
    )
from rest_framework.response import Response

from .models import Membership, Team
from .permissions import IsTeamMemberOrManager
from .serializers import (
    TeamOwnershipTransferSerializer,
    TeamMembershipRoleUpdateSerializer,
    TeamMembershipCreateSerializer,
    TeamMembershipSerializer,
    TeamSerializer
)


class TeamListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            Team.objects
            .select_related("created_by")
            .annotate(
                member_count_value=Count(
                    "memberships",
                    distinct=True,
                )
            )
            .filter(members=self.request.user)
            .order_by("-created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        team = serializer.save(
            created_by=self.request.user,
        )

        Membership.objects.create(
            team=team,
            user=self.request.user,
            role=Membership.Role.OWNER,
        )


class TeamDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TeamSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        IsTeamMemberOrManager,
    )

    http_method_names = (
        "get",
        "patch",
        "head",
        "options",
    )

    def get_queryset(self):
        return (
            Team.objects
            .select_related("created_by")
            .annotate(
                member_count_value=Count(
                    "memberships",
                    distinct=True,
                )
            )
            .filter(members=self.request.user)
        )

class TeamMembershipListView(
    generics.ListCreateAPIView
):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_team(self):
        if not hasattr(self, "_team"):
            self._team = get_object_or_404(
                Team.objects.filter(
                    members=self.request.user,
                ),
                pk=self.kwargs["team_id"],
            )

        return self._team

    def get_queryset(self):
        return (
            Membership.objects
            .filter(team=self.get_team())
            .select_related("user")
            .order_by("joined_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamMembershipCreateSerializer

        return TeamMembershipSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["team"] = self.get_team()

        return context

    def create(self, request, *args, **kwargs):
        team = self.get_team()

        requester_membership = Membership.objects.get(
            team=team,
            user=request.user,
        )

        if requester_membership.role not in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }:
            raise PermissionDenied(
                "No tienes permiso para agregar miembros."
            )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        role = serializer.validated_data["role"]

        if (
            requester_membership.role
            == Membership.Role.ADMIN
            and role != Membership.Role.MEMBER
        ):
            raise PermissionDenied(
                "Un administrador solo puede agregar miembros."
            )

        membership = Membership.objects.create(
            team=team,
            user=serializer.validated_data["user"],
            role=role,
        )

        output_serializer = TeamMembershipSerializer(
            membership,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

class TeamMembershipRoleUpdateView(
    generics.GenericAPIView
):
    serializer_class = TeamMembershipRoleUpdateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    http_method_names = (
        "patch",
        "delete",
        "head",
        "options",
    )

    def get_team(self):
        return get_object_or_404(
            Team.objects.filter(
                members=self.request.user,
            ),
            pk=self.kwargs["team_id"],
        )

    def patch(self, request, *args, **kwargs):
        team = self.get_team()

        requester_membership = Membership.objects.get(
            team=team,
            user=request.user,
        )

        if (
            requester_membership.role
            != Membership.Role.OWNER
        ):
            raise PermissionDenied(
                "Solo el propietario puede cambiar roles."
            )

        target_membership = get_object_or_404(
            Membership.objects.select_related("user"),
            team=team,
            user_id=self.kwargs["user_id"],
        )

        if (
            target_membership.role
            == Membership.Role.OWNER
        ):
            raise ValidationError(
                {
                    "role": (
                        "No puedes modificar el rol "
                        "del propietario."
                    )
                }
            )

        serializer = self.get_serializer(
            target_membership,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        output_serializer = TeamMembershipSerializer(
            target_membership,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        team = self.get_team()

        requester_membership = Membership.objects.get(
            team=team,
            user=request.user,
        )

        target_membership = get_object_or_404(
            Membership.objects.select_related("user"),
            team=team,
            user_id=self.kwargs["user_id"],
        )

        # Un usuario que no sea owner puede abandonar
        # voluntariamente el equipo.
        if target_membership.user_id == request.user.id:
            if requester_membership.role == Membership.Role.OWNER:
                raise ValidationError(
                    {
                        "detail": (
                            "El propietario no puede abandonar "
                            "el equipo sin transferir primero "
                            "la propiedad."
                        )
                    }
                )

            target_membership.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        # Un member no puede eliminar a otras personas.
        if requester_membership.role == Membership.Role.MEMBER:
            raise PermissionDenied(
                "No tienes permiso para eliminar miembros."
            )

        # Un admin solo puede eliminar usuarios con rol member.
        if requester_membership.role == Membership.Role.ADMIN:
            if target_membership.role != Membership.Role.MEMBER:
                raise PermissionDenied(
                    "Un administrador solo puede eliminar miembros."
                )

        target_membership.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

class TeamOwnershipTransferView(
    generics.GenericAPIView
):
    serializer_class = TeamOwnershipTransferSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    http_method_names = (
        "post",
        "head",
        "options",
    )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(
            Team.objects.filter(
                members=request.user,
            ),
            pk=self.kwargs["team_id"],
        )

        current_owner = get_object_or_404(
            Membership,
            team=team,
            user=request.user,
        )

        if current_owner.role != Membership.Role.OWNER:
            raise PermissionDenied(
                "Solo el propietario puede transferir la propiedad."
            )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_owner = get_object_or_404(
            Membership.objects.select_related("user"),
            team=team,
            user_id=serializer.validated_data["user_id"],
        )

        if new_owner.user_id == request.user.id:
            raise ValidationError(
                {
                    "user_id": (
                        "No puedes transferirte la propiedad "
                        "a ti mismo."
                    )
                }
            )

        current_owner.role = Membership.Role.ADMIN
        current_owner.save(
            update_fields=["role"],
        )

        new_owner.role = Membership.Role.OWNER
        new_owner.save(
            update_fields=["role"],
        )

        return Response(
            {
                "message": "Propiedad transferida correctamente.",
                "new_owner": TeamMembershipSerializer(
                    new_owner,
                ).data,
            },
            status=status.HTTP_200_OK,
        )