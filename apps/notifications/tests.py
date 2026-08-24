import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.teams.models import Membership, Team
from apps.users.models import User

from .models import Notification

@pytest.mark.django_db
def test_user_can_list_only_own_notifications():
    first_user = User.objects.create_user(
        username="notification_first_user",
        email="notification_first_user@example.com",
        password="Password123!",
    )

    second_user = User.objects.create_user(
        username="notification_second_user",
        email="notification_second_user@example.com",
        password="Password123!",
    )

    own_notification = Notification.objects.create(
        user=first_user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Tu propia notificación.",
    )

    Notification.objects.create(
        user=second_user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Notificación de otro usuario.",
    )

    client = APIClient()
    client.force_authenticate(user=first_user)

    response = client.get(
        reverse(
            "notifications:notification-list",
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == own_notification.pk
    assert (
        response.data[0]["message"]
        == "Tu propia notificación."
    )

def test_unauthenticated_user_cannot_list_notifications():
    client = APIClient()

    response = client.get(
        reverse(
            "notifications:notification-list",
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_user_can_mark_own_notification_as_read():
    user = User.objects.create_user(
        username="notification_read_user",
        email="notification_read_user@example.com",
        password="Password123!",
    )

    notification = Notification.objects.create(
        user=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Tienes una tarea nueva.",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        reverse(
            "notifications:notification-read",
            kwargs={
                "pk": notification.pk,
            },
        ),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["is_read"] is True
    assert response.data["read_at"] is not None

    notification.refresh_from_db()

    assert notification.is_read is True
    assert notification.read_at is not None

@pytest.mark.django_db
def test_user_cannot_mark_other_users_notification_as_read():
    owner = User.objects.create_user(
        username="notification_owner",
        email="notification_owner@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="notification_outsider",
        email="notification_outsider@example.com",
        password="Password123!",
    )

    notification = Notification.objects.create(
        user=owner,
        type=Notification.Type.TASK_ASSIGNED,
        message="Notificación privada.",
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.patch(
        reverse(
            "notifications:notification-read",
            kwargs={
                "pk": notification.pk,
            },
        ),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    notification.refresh_from_db()

    assert notification.is_read is False
    assert notification.read_at is None

@pytest.mark.django_db
def test_mark_notification_as_read_is_idempotent():
    user = User.objects.create_user(
        username="notification_idempotent_user",
        email="notification_idempotent_user@example.com",
        password="Password123!",
    )

    notification = Notification.objects.create(
        user=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Notificación idempotente.",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse(
        "notifications:notification-read",
        kwargs={
            "pk": notification.pk,
        },
    )

    first_response = client.patch(
        url,
        {},
        format="json",
    )

    assert first_response.status_code == status.HTTP_200_OK

    notification.refresh_from_db()

    first_read_at = notification.read_at

    second_response = client.patch(
        url,
        {},
        format="json",
    )

    assert second_response.status_code == status.HTTP_200_OK

    notification.refresh_from_db()

    assert notification.is_read is True
    assert notification.read_at == first_read_at

@pytest.mark.django_db
def test_assigning_task_on_creation_creates_notification():
    owner = User.objects.create_user(
        username="owner_task_assignment_notification",
        email="owner_task_assignment_notification@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_task_assignment_notification",
        email="member_task_assignment_notification@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo notificación asignación",
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
        name="Proyecto notificación asignación",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "title": "Implementar JWT",
            "assigned_to": member.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    notification = Notification.objects.get(
        user=member,
    )

    assert notification.type == Notification.Type.TASK_ASSIGNED
    assert notification.task_id == response.data["id"]
    assert notification.is_read is False
    assert notification.read_at is None
    assert "Implementar JWT" in notification.message

@pytest.mark.django_db
def test_creating_unassigned_task_does_not_create_notification():
    owner = User.objects.create_user(
        username="owner_unassigned_notification",
        email="owner_unassigned_notification@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tarea sin asignar",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tarea sin asignar",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "title": "Tarea pendiente de asignación",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Notification.objects.count() == 0

@pytest.mark.django_db
def test_reassigning_task_creates_notification_for_new_assignee():
    owner = User.objects.create_user(
        username="owner_task_reassignment",
        email="owner_task_reassignment@example.com",
        password="Password123!",
    )

    first_member = User.objects.create_user(
        username="first_task_assignee",
        email="first_task_assignee@example.com",
        password="Password123!",
    )

    second_member = User.objects.create_user(
        username="second_task_assignee",
        email="second_task_assignee@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo reasignación",
        created_by=owner,
    )

    for user, role in (
        (owner, Membership.Role.OWNER),
        (first_member, Membership.Role.MEMBER),
        (second_member, Membership.Role.MEMBER),
    ):
        Membership.objects.create(
            team=team,
            user=user,
            role=role,
        )

    project = Project.objects.create(
        team=team,
        name="Proyecto reasignación",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea reasignable",
        assigned_to=first_member,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": task.pk,
            },
        ),
        {
            "assigned_to": second_member.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert Notification.objects.filter(
        user=second_member,
        task=task,
        type=Notification.Type.TASK_ASSIGNED,
    ).count() == 1

    assert Notification.objects.filter(
        user=first_member,
    ).count() == 0

@pytest.mark.django_db
def test_updating_task_without_changing_assignee_does_not_duplicate_notification():
    owner = User.objects.create_user(
        username="owner_no_duplicate_notification",
        email="owner_no_duplicate_notification@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_no_duplicate_notification",
        email="member_no_duplicate_notification@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo sin duplicados",
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
        name="Proyecto sin duplicados",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea existente",
        assigned_to=member,
        priority=Task.Priority.MEDIUM,
        created_by=owner,
    )

    Notification.objects.create(
        user=member,
        type=Notification.Type.TASK_ASSIGNED,
        message='Te asignaron la tarea "Tarea existente".',
        task=task,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": task.pk,
            },
        ),
        {
            "priority": Task.Priority.HIGH,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert Notification.objects.filter(
        user=member,
        task=task,
        type=Notification.Type.TASK_ASSIGNED,
    ).count() == 1

@pytest.mark.django_db
def test_assigning_task_to_self_does_not_create_notification():
    owner = User.objects.create_user(
        username="owner_self_assignment",
        email="owner_self_assignment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo autoasignación",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto autoasignación",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "title": "Mi propia tarea",
            "assigned_to": owner.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert Notification.objects.count() == 0

@pytest.mark.django_db
def test_comment_creates_notifications_for_task_creator_and_assignee():
    owner = User.objects.create_user(
        username="comment_notification_owner",
        email="comment_notification_owner@example.com",
        password="Password123!",
    )

    assignee = User.objects.create_user(
        username="comment_notification_assignee",
        email="comment_notification_assignee@example.com",
        password="Password123!",
    )

    commenter = User.objects.create_user(
        username="comment_notification_author",
        email="comment_notification_author@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo notificaciones comentarios",
        created_by=owner,
    )

    for user, role in (
        (owner, Membership.Role.OWNER),
        (assignee, Membership.Role.MEMBER),
        (commenter, Membership.Role.MEMBER),
    ):
        Membership.objects.create(
            team=team,
            user=user,
            role=role,
        )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentarios",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Implementar comentarios",
        assigned_to=assignee,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=commenter)

    response = client.post(
        (
            f"/api/teams/{team.pk}/"
            f"projects/{project.pk}/"
            f"tasks/{task.pk}/comments/"
        ),
        {
            "content": "Ya revisé esta tarea.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    notifications = Notification.objects.filter(
        type=Notification.Type.COMMENT_CREATED,
        task=task,
    )

    assert notifications.count() == 2

    recipient_ids = set(
        notifications.values_list(
            "user_id",
            flat=True,
        )
    )

    assert recipient_ids == {
        owner.pk,
        assignee.pk,
    }

    assert commenter.pk not in recipient_ids

@pytest.mark.django_db
def test_comment_author_does_not_receive_own_notification():
    owner = User.objects.create_user(
        username="comment_self_owner",
        email="comment_self_owner@example.com",
        password="Password123!",
    )

    assignee = User.objects.create_user(
        username="comment_self_assignee",
        email="comment_self_assignee@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentario propio",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=assignee,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto comentario propio",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea comentada por responsable",
        assigned_to=assignee,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=assignee)

    response = client.post(
        (
            f"/api/teams/{team.pk}/"
            f"projects/{project.pk}/"
            f"tasks/{task.pk}/comments/"
        ),
        {
            "content": "Estoy trabajando en esto.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert Notification.objects.filter(
        user=owner,
        type=Notification.Type.COMMENT_CREATED,
        task=task,
    ).count() == 1

    assert Notification.objects.filter(
        user=assignee,
        type=Notification.Type.COMMENT_CREATED,
        task=task,
    ).count() == 0

@pytest.mark.django_db
def test_comment_does_not_duplicate_notification_when_creator_is_assignee():
    owner = User.objects.create_user(
        username="comment_duplicate_owner",
        email="comment_duplicate_owner@example.com",
        password="Password123!",
    )

    commenter = User.objects.create_user(
        username="comment_duplicate_author",
        email="comment_duplicate_author@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo evitar duplicados",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=commenter,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto evitar duplicados",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea mismo creador y responsable",
        created_by=owner,
        assigned_to=owner,
    )

    client = APIClient()
    client.force_authenticate(user=commenter)

    response = client.post(
        (
            f"/api/teams/{team.pk}/"
            f"projects/{project.pk}/"
            f"tasks/{task.pk}/comments/"
        ),
        {
            "content": "Comentario sin duplicados.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert Notification.objects.filter(
        user=owner,
        task=task,
        type=Notification.Type.COMMENT_CREATED,
    ).count() == 1

@pytest.mark.django_db
def test_comment_on_unassigned_task_notifies_task_creator():
    owner = User.objects.create_user(
        username="unassigned_comment_owner",
        email="unassigned_comment_owner@example.com",
        password="Password123!",
    )

    commenter = User.objects.create_user(
        username="unassigned_comment_author",
        email="unassigned_comment_author@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo comentario sin responsable",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=commenter,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto sin responsable",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea todavía sin asignar",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=commenter)

    response = client.post(
        (
            f"/api/teams/{team.pk}/"
            f"projects/{project.pk}/"
            f"tasks/{task.pk}/comments/"
        ),
        {
            "content": "Hay que revisar esta tarea.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    notification = Notification.objects.get(
        type=Notification.Type.COMMENT_CREATED,
        task=task,
    )

    assert notification.user_id == owner.pk

@pytest.mark.django_db
def test_comment_creates_no_notification_when_actor_is_only_recipient():
    owner = User.objects.create_user(
        username="comment_only_recipient",
        email="comment_only_recipient@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo sin destinatario",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto sin destinatario",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea personal",
        created_by=owner,
        assigned_to=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        (
            f"/api/teams/{team.pk}/"
            f"projects/{project.pk}/"
            f"tasks/{task.pk}/comments/"
        ),
        {
            "content": "Mi propio comentario.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert Notification.objects.filter(
        type=Notification.Type.COMMENT_CREATED,
        task=task,
    ).count() == 0

