from django.db import transaction
from django.db.models import Count
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from .models import Membership, Team
from .permissions import IsTeamMemberOrManager
from .serializers import TeamMembershipSerializer,TeamSerializer


class TeamListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            Team.objects
            .select_related("created_by")
            .annotate(
                member_count_value=Count(
                    "memberships",
                    distinct=True,
                )
            )
            .filter(members=self.request.user)
            .order_by("-created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        team = serializer.save(
            created_by=self.request.user,
        )

        Membership.objects.create(
            team=team,
            user=self.request.user,
            role=Membership.Role.OWNER,
        )


class TeamDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TeamSerializer

    permission_classes = (
        permissions.IsAuthenticated,
        IsTeamMemberOrManager,
    )

    http_method_names = (
        "get",
        "patch",
        "head",
        "options",
    )

    def get_queryset(self):
        return (
            Team.objects
            .select_related("created_by")
            .annotate(
                member_count_value=Count(
                    "memberships",
                    distinct=True,
                )
            )
            .filter(members=self.request.user)
        )

class TeamMembershipListView(generics.ListAPIView):
    serializer_class = TeamMembershipSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        team = get_object_or_404(
            Team.objects.filter(
                members=self.request.user,
            ),
            pk=self.kwargs["team_id"],
        )

        return (
            Membership.objects
            .filter(team=team)
            .select_related("user")
            .order_by("joined_at")
        )