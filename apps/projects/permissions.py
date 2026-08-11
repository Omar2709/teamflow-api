from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.teams.models import Membership


class CanAccessProject(BasePermission):
    message = "No tienes permiso para modificar este proyecto."

    def has_object_permission(self, request, view, project):
        membership = (
            Membership.objects
            .filter(
                team=project.team,
                user=request.user,
            )
            .only("role")
            .first()
        )

        if membership is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        return membership.role in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }
    