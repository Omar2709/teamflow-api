from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.projects.models import Project
from apps.teams.models import Membership

from .models import Task
from .serializers import TaskSerializer


class ProjectTaskListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = TaskSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_project(self):
        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                Project.objects
                .select_related("team")
                .filter(
                    team_id=self.kwargs["team_id"],
                    team__members=self.request.user,
                ),
                pk=self.kwargs["project_id"],
            )

        return self._project

    def get_queryset(self):
        return (
            Task.objects
            .filter(
                project=self.get_project(),
            )
            .select_related(
                "project",
                "assigned_to",
                "created_by",
            )
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()

        project = self.get_project()

        context["project"] = project
        context["team"] = project.team

        return context

    def create(self, request, *args, **kwargs):
        project = self.get_project()

        membership = Membership.objects.get(
            team=project.team,
            user=request.user,
        )

        if membership.role not in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }:
            raise PermissionDenied(
                "No tienes permiso para crear tareas."
            )

        return super().create(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        serializer.save(
            project=self.get_project(),
            created_by=self.request.user,
        )