from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.teams.models import Membership


class CanAccessComment(BasePermission):
    message = "No tienes permiso para modificar este comentario."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        comment = obj

        membership = (
            Membership.objects
            .filter(
                team=comment.task.project.team,
                user=request.user,
            )
            .only("role")
            .first()
        )

        if membership is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "PATCH":
            return comment.author == request.user

        if request.method == "DELETE":
            return (
                comment.author == request.user
                or membership.role
                in {
                    Membership.Role.OWNER,
                    Membership.Role.ADMIN,
                }
            )

        return False