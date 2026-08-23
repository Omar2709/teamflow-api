from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.tasks.models import Task

from .models import Team


class TeamDashboardView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, team_id):
        team = get_object_or_404(
            Team.objects.filter(
                members=request.user,
            ),
            pk=team_id,
        )

        project_count = Project.objects.filter(
            team=team,
        ).count()

        today = timezone.localdate()

        task_metrics = (
            Task.objects
            .filter(
                project__team=team,
            )
            .aggregate(
                total=Count("pk"),
                todo=Count(
                    "pk",
                    filter=Q(
                        status=Task.Status.TODO,
                    ),
                ),
                in_progress=Count(
                    "pk",
                    filter=Q(
                        status=Task.Status.IN_PROGRESS,
                    ),
                ),
                done=Count(
                    "pk",
                    filter=Q(
                        status=Task.Status.DONE,
                    ),
                ),
                overdue=Count(
                    "pk",
                    filter=(
                        Q(due_date__lt=today)
                        & ~Q(
                            status=Task.Status.DONE,
                        )
                    ),
                ),
            )
        )

        return Response(
            {
                "team": {
                    "id": team.pk,
                    "name": team.name,
                },
                "projects": {
                    "total": project_count,
                },
                "tasks": task_metrics,
            }
        )