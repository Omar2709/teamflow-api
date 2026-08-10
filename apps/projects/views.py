from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.teams.models import Membership, Team

from .models import Project
from .serializers import ProjectSerializer


class TeamProjectListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = ProjectSerializer
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
            Project.objects
            .filter(team=self.get_team())
            .select_related(
                "team",
                "created_by",
            )
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["team"] = self.get_team()

        return context

    def create(self, request, *args, **kwargs):
        team = self.get_team()

        membership = Membership.objects.get(
            team=team,
            user=request.user,
        )

        if membership.role not in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }:
            raise PermissionDenied(
                "No tienes permiso para crear proyectos."
            )

        return super().create(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        serializer.save(
            team=self.get_team(),
            created_by=self.request.user,
        )