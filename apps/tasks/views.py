from typing import cast

from collections.abc import Mapping
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.notifications.services import (
    create_task_assignment_notification,
)
from apps.projects.models import Project
from apps.teams.models import Membership
from apps.users.models import User

from .models import Task
from .pagination import TaskPagination
from .permissions import CanAccessTask
from .serializers import TaskSerializer

class ProjectTaskListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = TaskSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    pagination_class = TaskPagination

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_fields =(
        "status",
        "priority",
        "assigned_to",
    )

    search_fields =(
        "title",
        "description",
    )

    ordering_fields =(
        "due_date",
        "created_at",
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
        if getattr(
            self,
            "swagger_fake_view",
            False,
        ):
            return Task.objects.none()
        
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
        context = dict(super().get_serializer_context())

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

    @transaction.atomic
    def perform_create(self, serializer):
        task = serializer.save(
            project=self.get_project(),
            created_by=self.request.user,
        )

        actor = cast(User, self.request.user)

        create_task_assignment_notification(
            task=task,
            actor=actor,
        )


class TaskDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TaskSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        CanAccessTask,
    )

    http_method_names = [
        "get",
        "patch",
        "delete",
        "head",
        "options",
    ]

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
                "project__team",
                "assigned_to",
                "created_by",
            )
        )

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        task = self.get_object()

        membership = Membership.objects.get(
            team=task.project.team,
            user=request.user,
        )

        if membership.role == Membership.Role.MEMBER:
            if not isinstance(request.data, Mapping):
                raise PermissionDenied(
                    "Los datos enviados deben ser un objeto."
                )
            allowed_fields = {"status"}
            received_fields = set(request.data.keys())

            if not received_fields.issubset(allowed_fields):
                raise PermissionDenied(
                    "Un miembro asignado solo puede cambiar "
                    "el estado de la tarea."
                )

        return super().partial_update(
            request,
            *args,
            **kwargs,
        )

    def get_serializer_context(self):
        context = dict(
            super().get_serializer_context()
        )

        project = self.get_project()

        context["project"] = project
        context["team"] = project.team

        return context

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance

        assert instance is not None

        previous_assignee_id = (
            instance.assigned_to.pk
            if instance.assigned_to is not None
            else None
        )

        task = serializer.save()

        actor = cast(User, self.request.user)

        create_task_assignment_notification(
            task=task,
            actor=actor,
            previous_assignee_id=previous_assignee_id,
        )
