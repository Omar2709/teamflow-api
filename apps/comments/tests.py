import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.teams.models import Membership, Team
from apps.users.models import User

from .models import Comment

@pytest.mark.django_db
def test_team_member_can_create_task_comment():
    owner = User.objects.create_user(
        username="owner_create_comment",
        email="owner_create_comment@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_create_comment",
        email="member_create_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea comentable",
        created_by=owner,
        assigned_to=member,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "content": "   Ya terminé esta parte.   ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["content"] == "Ya terminé esta parte."
    assert response.data["task"] == task.pk
    assert response.data["author"]["id"] == member.pk

    comment = Comment.objects.get(
        pk=response.data["id"],
    )

    assert comment.task == task
    assert comment.author == member
    assert comment.content == "Ya terminé esta parte."

@pytest.mark.django_db
def test_team_member_can_list_task_comments():
    owner = User.objects.create_user(
        username="owner_list_comments",
        email="owner_list_comments@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_list_comments",
        email="member_list_comments@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo listado comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto listado comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea con comentarios",
        created_by=owner,
    )

    first_comment = Comment.objects.create(
        task=task,
        author=owner,
        content="Primer comentario",
    )

    second_comment = Comment.objects.create(
        task=task,
        author=member,
        content="Segundo comentario",
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2

    assert response.data["results"][0]["id"] == first_comment.pk
    assert response.data["results"][1]["id"] == second_comment.pk

@pytest.mark.django_db
def test_comment_list_only_returns_comments_from_requested_task():
    owner = User.objects.create_user(
        username="owner_comment_isolation",
        email="owner_comment_isolation@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo aislamiento comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto aislamiento comentarios",
        created_by=owner,
    )

    first_task = Task.objects.create(
        project=project,
        title="Primera tarea",
        created_by=owner,
    )

    second_task = Task.objects.create(
        project=project,
        title="Segunda tarea",
        created_by=owner,
    )

    first_comment = Comment.objects.create(
        task=first_task,
        author=owner,
        content="Comentario primera tarea",
    )

    second_comment = Comment.objects.create(
        task=second_task,
        author=owner,
        content="Comentario segunda tarea",
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": first_task.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1

    assert response.data["results"][0]["id"] == first_comment.pk

    returned_ids = {
        comment["id"]
        for comment in response.data["results"]
    }

    assert second_comment.pk not in returned_ids

@pytest.mark.django_db
def test_outsider_cannot_create_task_comment():
    owner = User.objects.create_user(
        username="owner_private_comment",
        email="owner_private_comment@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_create_comment",
        email="outsider_create_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentarios privados",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentarios privados",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea privada",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.post(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "content": "No debería poder comentar.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_task_comment_rejects_content_with_only_spaces():
    owner = User.objects.create_user(
        username="owner_blank_comment",
        email="owner_blank_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo validación comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto validación comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea validación comentario",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "content": "           ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "content" in response.data

    assert Comment.objects.count() == 0

def test_unauthenticated_user_cannot_access_task_comments():
    client = APIClient()

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": 1,
                "project_id": 1,
                "task_id": 1,
            },
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_team_member_can_retrieve_comment_detail():
    owner = User.objects.create_user(
        username="owner_comment_detail",
        email="owner_comment_detail@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_comment_detail",
        email="member_comment_detail@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo detalle comentario",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto detalle comentario",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea detalle comentario",
        created_by=owner,
    )

    comment = Comment.objects.create(
        task=task,
        author=owner,
        content="Comentario visible.",
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": comment.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == comment.pk
    assert response.data["task"] == task.pk
    assert response.data["content"] == "Comentario visible."
    assert response.data["author"]["id"] == owner.pk

@pytest.mark.django_db
def test_comment_author_can_update_own_comment():
    owner = User.objects.create_user(
        username="owner_update_own_comment",
        email="owner_update_own_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo edición comentario",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto edición comentario",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea edición comentario",
        created_by=owner,
    )

    comment = Comment.objects.create(
        task=task,
        author=owner,
        content="Contenido original.",
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": comment.pk,
            },
        ),
        {
            "content": "   Contenido actualizado.   ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["content"] == "Contenido actualizado."

    comment.refresh_from_db()

    assert comment.content == "Contenido actualizado."
    assert comment.author == owner
    assert comment.task == task

@pytest.mark.django_db
def test_other_team_member_cannot_update_comment():
    owner = User.objects.create_user(
        username="owner_other_member_comment",
        email="owner_other_member_comment@example.com",
        password="Password123!",
    )

    author = User.objects.create_user(
        username="author_protected_comment",
        email="author_protected_comment@example.com",
        password="Password123!",
    )

    other_member = User.objects.create_user(
        username="other_member_protected_comment",
        email="other_member_protected_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentario protegido",
        created_by=owner,
    )

    for user, role in (
        (owner, Membership.Role.OWNER),
        (author, Membership.Role.MEMBER),
        (other_member, Membership.Role.MEMBER),
    ):
        Membership.objects.create(
            team=team,
            user=user,
            role=role,
        )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentario protegido",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea comentario protegido",
        created_by=owner,
    )

    comment = Comment.objects.create(
        task=task,
        author=author,
        content="No debe ser modificado.",
    )

    client = APIClient()
    client.force_authenticate(user=other_member)

    response = client.patch(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": comment.pk,
            },
        ),
        {
            "content": "Intento de modificación.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    comment.refresh_from_db()

    assert comment.content == "No debe ser modificado."

@pytest.mark.django_db
def test_comment_author_can_delete_own_comment():
    owner = User.objects.create_user(
        username="owner_delete_own_comment",
        email="owner_delete_own_comment@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_delete_own_comment",
        email="member_delete_own_comment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo eliminar comentario propio",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto eliminar comentario propio",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea eliminación comentario",
        created_by=owner,
    )

    comment = Comment.objects.create(
        task=task,
        author=member,
        content="Comentario que será eliminado.",
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.delete(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": comment.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Comment.objects.filter(
        pk=comment.pk,
    ).exists()

@pytest.mark.django_db
def test_team_owner_and_admin_can_delete_other_users_comments():
    owner = User.objects.create_user(
        username="owner_moderate_comments",
        email="owner_moderate_comments@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_moderate_comments",
        email="admin_moderate_comments@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_moderated_comments",
        email="member_moderated_comments@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo moderación comentarios",
        created_by=owner,
    )

    for user, role in (
        (owner, Membership.Role.OWNER),
        (admin, Membership.Role.ADMIN),
        (member, Membership.Role.MEMBER),
    ):
        Membership.objects.create(
            team=team,
            user=user,
            role=role,
        )

    project = Project.objects.create(
        team=team,
        name="Proyecto moderación comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea moderación comentarios",
        created_by=owner,
    )

    owner_target = Comment.objects.create(
        task=task,
        author=member,
        content="Comentario eliminado por owner.",
    )

    admin_target = Comment.objects.create(
        task=task,
        author=member,
        content="Comentario eliminado por admin.",
    )

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)

    owner_response = owner_client.delete(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": owner_target.pk,
            },
        )
    )

    assert owner_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(
        pk=owner_target.pk,
    ).exists()

    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)

    admin_response = admin_client.delete(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": admin_target.pk,
            },
        )
    )

    assert admin_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(
        pk=admin_target.pk,
    ).exists()

@pytest.mark.django_db
def test_outsider_cannot_retrieve_comment_detail():
    owner = User.objects.create_user(
        username="owner_private_comment_detail",
        email="owner_private_comment_detail@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_comment_detail",
        email="outsider_comment_detail@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentario privado detalle",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentario privado detalle",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea comentario privado detalle",
        created_by=owner,
    )

    comment = Comment.objects.create(
        task=task,
        author=owner,
        content="Comentario privado.",
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.get(
        reverse(
            "comments:comment-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
                "pk": comment.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_task_comment_list_is_paginated():
    owner = User.objects.create_user(
        username="owner_paginated_comments",
        email="owner_paginated_comments@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo paginación comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto paginación comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea paginación comentarios",
        created_by=owner,
    )

    for index in range(12):
        Comment.objects.create(
            task=task,
            author=owner,
            content=f"Comentario {index + 1}",
        )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 12
    assert len(response.data["results"]) == 10

    assert response.data["next"] is not None
    assert response.data["previous"] is None

@pytest.mark.django_db
def test_task_comment_list_can_return_second_page():
    owner = User.objects.create_user(
        username="owner_second_comment_page",
        email="owner_second_comment_page@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo segunda página comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto segunda página comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea segunda página comentarios",
        created_by=owner,
    )

    for index in range(12):
        Comment.objects.create(
            task=task,
            author=owner,
            content=f"Comentario paginado {index + 1}",
        )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "page": 2,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 12
    assert len(response.data["results"]) == 2

    assert response.data["next"] is None
    assert response.data["previous"] is not None

@pytest.mark.django_db
def test_task_comment_list_accepts_custom_page_size():
    owner = User.objects.create_user(
        username="owner_comment_page_size",
        email="owner_comment_page_size@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tamaño página comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tamaño página comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea tamaño página comentarios",
        created_by=owner,
    )

    for index in range(8):
        Comment.objects.create(
            task=task,
            author=owner,
            content=f"Comentario tamaño {index + 1}",
        )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "page_size": 3,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 8
    assert len(response.data["results"]) == 3
    assert response.data["next"] is not None

@pytest.mark.django_db
def test_task_comment_page_size_is_limited_to_maximum():
    owner = User.objects.create_user(
        username="owner_comment_max_page_size",
        email="owner_comment_max_page_size@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo máximo comentarios",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto máximo comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea máximo comentarios",
        created_by=owner,
    )

    for index in range(55):
        Comment.objects.create(
            task=task,
            author=owner,
            content=f"Comentario límite {index + 1}",
        )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "comments:task-comment-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "task_id": task.pk,
            },
        ),
        {
            "page_size": 1000,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["count"] == 55
    assert len(response.data["results"]) == 50
    assert response.data["next"] is not None

