from datetime import timedelta

from drf_spectacular.utils import extend_schema
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TeamDashboardResponseSerializer

from apps.projects.models import Project
from apps.tasks.models import Task

from .models import Membership, Team


class TeamDashboardView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    @extend_schema(
        tags=["teams"],
        summary="Obtener dashboard del equipo",
        description=(
            "Devuelve métricas agregadas del equipo, "
            "sus proyectos, tareas y tareas asignadas "
            "al usuario autenticado."
        ),
        responses={
            200: TeamDashboardResponseSerializer,
        },
    )

    def get(self, request, team_id):
        team = get_object_or_404(
            Team.objects.filter(
                members=request.user,
            ),
            pk=team_id,
        )

        today = timezone.localdate()
        due_soon_limit = today + timedelta(days=7)

        member_count = Membership.objects.filter(
            team=team,
        ).count()

        tasks = Task.objects.filter(
            project__team=team,
        )

        task_metrics = tasks.aggregate(
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
            due_soon=Count(
                "pk",
                filter=(
                    Q(
                        due_date__gt=today,
                        due_date__lte=due_soon_limit,
                    )
                    & ~Q(
                        status=Task.Status.DONE,
                    )
                ),
            ),
            unassigned=Count(
                "pk",
                filter=Q(
                    assigned_to__isnull=True,
                ),
            ),
            low=Count(
                "pk",
                filter=Q(
                    priority=Task.Priority.LOW,
                ),
            ),
            medium=Count(
                "pk",
                filter=Q(
                    priority=Task.Priority.MEDIUM,
                ),
            ),
            high=Count(
                "pk",
                filter=Q(
                    priority=Task.Priority.HIGH,
                ),
            ),
        )

        my_tasks = tasks.filter(
            assigned_to=request.user,
        )

        my_task_metrics = my_tasks.aggregate(
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
            due_soon=Count(
                "pk",
                filter=(
                    Q(
                        due_date__gt=today,
                        due_date__lte=due_soon_limit,
                    )
                    & ~Q(
                        status=Task.Status.DONE,
                    )
                ),
            ),
        )

        projects = list(
            Project.objects
            .filter(
                team=team,
            )
            .annotate(
                task_total=Count("tasks"),
                task_todo=Count(
                    "tasks",
                    filter=Q(
                        tasks__status=Task.Status.TODO,
                    ),
                ),
                task_in_progress=Count(
                    "tasks",
                    filter=Q(
                        tasks__status=Task.Status.IN_PROGRESS,
                    ),
                ),
                task_done=Count(
                    "tasks",
                    filter=Q(
                        tasks__status=Task.Status.DONE,
                    ),
                ),
            )
            .order_by("name")
        )

        project_breakdown = [
            {
                "id": project.pk,
                "name": project.name,
                "tasks": {
                    "total": getattr(project, "task_total"),
                    "todo": getattr(project, "task_todo"),
                    "in_progress": (
                        getattr(project, "task_in_progress")
                    ),
                    "done": getattr(project, "task_done"),
                },
            }
            for project in projects
        ]

        return Response(
            {
                "team": {
                    "id": team.pk,
                    "name": team.name,
                    "members": member_count,
                },
                "projects": {
                    "total": len(projects),
                    "breakdown": project_breakdown,
                },
                "tasks": task_metrics,
                "my_tasks": my_task_metrics,
            }
        )