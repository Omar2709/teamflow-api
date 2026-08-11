from django.urls import path

from .views import (
    TeamProjectListCreateView,
    ProjectDetailView
)


app_name = "projects"


urlpatterns = [
    path(
        "teams/<int:team_id>/projects/",
        TeamProjectListCreateView.as_view(),
        name="team-project-list-create",
    ),
    path(
        "teams/<int:team_id>/projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    )
]