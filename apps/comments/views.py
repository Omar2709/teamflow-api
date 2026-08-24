from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from django.db import transaction

from apps.notifications.services import (
    create_comment_notifications,
)
from apps.tasks.models import Task

from .models import Comment
from .serializers import CommentSerializer
from .permissions import CanAccessComment
from .pagination import CommentPagination


class TaskCommentListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = CommentSerializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    pagination_class = CommentPagination

    def get_task(self):
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(
                Task.objects
                .select_related(
                    "project",
                    "project__team",
                )
                .filter(
                    project_id=self.kwargs["project_id"],
                    project__team_id=self.kwargs["team_id"],
                    project__team__members=self.request.user,
                ),
                pk=self.kwargs["task_id"],
            )

        return self._task

    def get_queryset(self):
        return (
            Comment.objects
            .filter(
                task=self.get_task(),
            )
            .select_related(
                "task",
                "author",
            )
            .order_by("created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        comment = serializer.save(
            task=self.get_task(),
            author=self.request.user,
        )

        create_comment_notifications(
            comment=comment,
            actor=self.request.user,
        )

class CommentDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = CommentSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        CanAccessComment,
    )

    http_method_names = (
        "get",
        "patch",
        "delete",
        "head",
        "options",
    )

    def get_task(self):
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(
                Task.objects
                .select_related(
                    "project",
                    "project__team",
                )
                .filter(
                    project_id=self.kwargs["project_id"],
                    project__team_id=self.kwargs["team_id"],
                    project__team__members=self.request.user,
                ),
                pk=self.kwargs["task_id"],
            )

        return self._task

    def get_queryset(self):
        return (
            Comment.objects
            .filter(
                task=self.get_task(),
            )
            .select_related(
                "task",
                "task__project",
                "task__project__team",
                "author",
            )
        )