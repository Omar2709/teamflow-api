from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.teams.models import Membership


class CanAccessTask(BasePermission):
    message = "No tienes permiso para modificar esta tarea."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        task = obj

        membership = (
            Membership.objects
            .filter(
                team=task.project.team,
                user=request.user,
            )
            .only("role")
            .first()
        )

        if membership is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if membership.role in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }:
            return True

        if (
            request.method == "PATCH"
            and task.assigned_to_id == request.user.pk
        ):
            return True

        return False