from django.urls import path

from .views import TeamProjectListCreateView


app_name = "projects"


urlpatterns = [
    path(
        "teams/<int:team_id>/projects/",
        TeamProjectListCreateView.as_view(),
        name="team-project-list-create",
    ),
]