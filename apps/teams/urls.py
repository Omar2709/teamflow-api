from django.urls import path

from .views import (
    TeamDetailView, 
    TeamListCreateView, 
    TeamMembershipListView,
    TeamMembershipRoleUpdateView,
)


app_name = "teams"

urlpatterns = [
    path(
        "teams/",
        TeamListCreateView.as_view(),
        name="team-list-create",
    ),
    path(
        "teams/<int:pk>/",
        TeamDetailView.as_view(),
        name="team-detail",
    ),
    path(
        "teams/<int:team_id>/members/",
        TeamMembershipListView.as_view(),
        name="team-members",
    ),
    path(
    "teams/<int:team_id>/members/<int:user_id>/",
    TeamMembershipRoleUpdateView.as_view(),
    name="team-member-detail",
    ),
]