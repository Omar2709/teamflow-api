from django.urls import path

from .views import (
    CommentDetailView,
    TaskCommentListCreateView,
)


app_name = "comments"


urlpatterns = [
    path(
        "teams/<int:team_id>/projects/"
        "<int:project_id>/tasks/"
        "<int:task_id>/comments/",
        TaskCommentListCreateView.as_view(),
        name="task-comment-list-create",
    ),
    path(
        "teams/<int:team_id>/projects/"
        "<int:project_id>/tasks/"
        "<int:task_id>/comments/<int:pk>/",
        CommentDetailView.as_view(),
        name="comment-detail",
    ),
]