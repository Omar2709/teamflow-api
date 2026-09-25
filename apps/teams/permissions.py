from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Membership


class IsTeamMemberOrManager(BasePermission):
    message = "No tienes permiso para modificar este equipo."

    def has_object_permission(self, request, view, obj):
        team = obj

        membership = team.memberships.filter(user=request.user).only("role").first()

        if membership is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        return membership.role in {
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        }
