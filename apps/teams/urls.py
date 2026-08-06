from django.urls import path

from .views import TeamDetailView, TeamListCreateView


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
]