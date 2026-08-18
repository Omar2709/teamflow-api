from django.urls import path

from .views import (
    ProjectTaskListCreateView, 
    TaskDetailView,
)


app_name = "tasks"


urlpatterns = [
    path(
        "teams/<int:team_id>/projects/"
        "<int:project_id>/tasks/",
        ProjectTaskListCreateView.as_view(),
        name="project-task-list-create",
    ),
    path(
        "tems/<int:team_id>/projects/"
        "<int:project_id>/tasks/<int:pk>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
]