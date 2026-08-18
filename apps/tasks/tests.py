import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.teams.models import Membership, Team
from apps.users.models import User

from .models import Task



@pytest.mark.django_db
def test_team_owner_can_create_task():
    owner = User.objects.create_user(
        username="owner_create_task",
        email="owner_create_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo creación tareas owner",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tareas owner",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "   Implementar    autenticación   ",
            "description": "Crear el sistema de login.",
            "priority": Task.Priority.HIGH,
            "due_date": "2026-08-20",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["title"] == "Implementar autenticación"
    assert response.data["description"] == "Crear el sistema de login."
    assert response.data["status"] == Task.Status.TODO
    assert response.data["priority"] == Task.Priority.HIGH
    assert response.data["assigned_to"] is None
    assert response.data["project"] == project.id
    assert response.data["created_by"]["id"] == owner.id
    assert response.data["due_date"] == "2026-08-20"

    task = Task.objects.get(
        id=response.data["id"],
    )

    assert task.project == project
    assert task.created_by == owner
    assert task.assigned_to is None
    assert task.status == Task.Status.TODO
    assert task.priority == Task.Priority.HIGH

@pytest.mark.django_db
def test_team_admin_can_create_task():
    owner = User.objects.create_user(
        username="owner_admin_create_task",
        email="owner_admin_create_task@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_create_task",
        email="admin_create_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo creación tareas admin",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=admin,
        role=Membership.Role.ADMIN,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tareas admin",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Tarea creada por admin",
            "description": "Creada por un administrador.",
            "priority": Task.Priority.MEDIUM,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["title"] == "Tarea creada por admin"
    assert response.data["project"] == project.id
    assert response.data["created_by"]["id"] == admin.id
    assert response.data["status"] == Task.Status.TODO
    assert response.data["priority"] == Task.Priority.MEDIUM

    task = Task.objects.get(
        id=response.data["id"],
    )

    assert task.project == project
    assert task.created_by == admin

@pytest.mark.django_db
def test_team_member_cannot_create_task():
    owner = User.objects.create_user(
        username="owner_member_create_task",
        email="owner_member_create_task@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_cannot_create_task",
        email="member_cannot_create_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tareas restringidas",
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
        name="Proyecto restringido",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Tarea no autorizada",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_outsider_cannot_create_task():
    owner = User.objects.create_user(
        username="owner_private_task",
        email="owner_private_task@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_create_task",
        email="outsider_create_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tareas privadas",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tareas privadas",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Intento externo",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_task():
    owner = User.objects.create_user(
        username="owner_unauthenticated_task",
        email="owner_unauthenticated_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tareas autenticadas",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tareas autenticadas",
        created_by=owner,
    )

    client = APIClient()

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Tarea anónima",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_team_member_can_list_project_tasks():
    owner = User.objects.create_user(
        username="owner_list_tasks",
        email="owner_list_tasks@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_list_tasks",
        email="member_list_tasks@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo listado tareas",
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
        name="Proyecto listado tareas",
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
        priority=Task.Priority.HIGH,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    returned_ids = {
        task["id"]
        for task in response.data
    }

    assert first_task.id in returned_ids
    assert second_task.id in returned_ids

@pytest.mark.django_db
def test_task_list_only_returns_tasks_from_requested_project():
    owner = User.objects.create_user(
        username="owner_project_task_isolation",
        email="owner_project_task_isolation@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo aislamiento tareas",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    first_project = Project.objects.create(
        team=team,
        name="Primer proyecto tareas",
        created_by=owner,
    )

    second_project = Project.objects.create(
        team=team,
        name="Segundo proyecto tareas",
        created_by=owner,
    )

    first_task = Task.objects.create(
        project=first_project,
        title="Tarea primer proyecto",
        created_by=owner,
    )

    second_task = Task.objects.create(
        project=second_project,
        title="Tarea segundo proyecto",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": first_project.id,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == first_task.id
    assert response.data[0]["project"] == first_project.id

    returned_ids = {
        task["id"]
        for task in response.data
    }

    assert second_task.id not in returned_ids

@pytest.mark.django_db
def test_task_creation_rejects_title_with_only_spaces():
    owner = User.objects.create_user(
        username="owner_blank_task_title",
        email="owner_blank_task_title@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo validación título tarea",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto validación título",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "        ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_task_creation_rejects_invalid_status_and_priority():
    owner = User.objects.create_user(
        username="owner_invalid_task_choices",
        email="owner_invalid_task_choices@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo validación opciones tarea",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto opciones tarea",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Tarea con valores inválidos",
            "status": "cancelled",
            "priority": "urgent",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "status" in response.data
    assert "priority" in response.data

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_task_assigned_user_must_belong_to_team():
    owner = User.objects.create_user(
        username="owner_task_assignment",
        email="owner_task_assignment@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_task_assignment",
        email="outsider_task_assignment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo asignación tareas",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto asignación segura",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.id,
                "project_id": project.id,
            },
        ),
        {
            "title": "Tarea con asignación inválida",
            "assigned_to": outsider.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "assigned_to" in response.data

    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_team_member_can_retrieve_task_detail():
    owner = User.objects.create_user(
        username="owner_task_detail",
        email="owner_task_detail@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_task_detail",
        email="member_task_detail@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo detalle tarea",
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
        name="Proyecto detalle tarea",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea consultable",
        description="Visible para miembros.",
        priority=Task.Priority.HIGH,
        created_by=owner,
        assigned_to=member,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": task.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == task.pk
    assert response.data["project"] == project.pk
    assert response.data["title"] == task.title
    assert response.data["description"] == task.description
    assert response.data["status"] == Task.Status.TODO
    assert response.data["priority"] == Task.Priority.HIGH
    assert response.data["assigned_to"] == member.pk
    assert response.data["created_by"]["id"] == owner.pk

@pytest.mark.django_db
def test_outsider_cannot_retrieve_task_detail():
    owner = User.objects.create_user(
        username="owner_private_task_detail",
        email="owner_private_task_detail@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_task_detail",
        email="outsider_task_detail@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tarea privada",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto tarea privada",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea privada",
        description="Solo miembros del equipo pueden verla.",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.get(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": task.pk,
            },
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data

def test_unauthenticated_user_cannot_retrieve_task_detail():
    client = APIClient()

    response = client.get(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": 1,
                "project_id": 1,
                "pk": 1,
            },
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_team_owner_can_update_task():
    owner = User.objects.create_user(
        username="owner_update_task",
        email="owner_update_task@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_assigned_update_task",
        email="member_assigned_update_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo actualización tarea owner",
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
        name="Proyecto actualización tarea owner",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea original",
        description="Descripción original.",
        status=Task.Status.TODO,
        priority=Task.Priority.MEDIUM,
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
            "title": "   Tarea    actualizada   ",
            "description": "Descripción actualizada.",
            "status": Task.Status.IN_PROGRESS,
            "priority": Task.Priority.HIGH,
            "assigned_to": member.pk,
            "due_date": "2026-08-30",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["title"] == "Tarea actualizada"
    assert response.data["description"] == "Descripción actualizada."
    assert response.data["status"] == Task.Status.IN_PROGRESS
    assert response.data["priority"] == Task.Priority.HIGH
    assert response.data["assigned_to"] == member.pk
    assert response.data["project"] == project.pk
    assert response.data["created_by"]["id"] == owner.pk
    assert response.data["due_date"] == "2026-08-30"

    task.refresh_from_db()

    assert task.title == "Tarea actualizada"
    assert task.description == "Descripción actualizada."
    assert task.status == Task.Status.IN_PROGRESS
    assert task.priority == Task.Priority.HIGH
    assert task.assigned_to == member
    assert task.project == project
    assert task.created_by == owner

@pytest.mark.django_db
def test_team_admin_can_update_task():
    owner = User.objects.create_user(
        username="owner_admin_update_task",
        email="owner_admin_update_task@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_update_task",
        email="admin_update_task@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_assigned_by_admin",
        email="member_assigned_by_admin@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo actualización tarea admin",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=admin,
        role=Membership.Role.ADMIN,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto actualización tarea admin",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea administrable",
        description="Descripción original.",
        status=Task.Status.TODO,
        priority=Task.Priority.LOW,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

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
            "title": "Tarea modificada por admin",
            "status": Task.Status.IN_PROGRESS,
            "priority": Task.Priority.HIGH,
            "assigned_to": member.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["title"] == "Tarea modificada por admin"
    assert response.data["status"] == Task.Status.IN_PROGRESS
    assert response.data["priority"] == Task.Priority.HIGH
    assert response.data["assigned_to"] == member.pk

    assert response.data["project"] == project.pk
    assert response.data["created_by"]["id"] == owner.pk

    task.refresh_from_db()

    assert task.title == "Tarea modificada por admin"
    assert task.status == Task.Status.IN_PROGRESS
    assert task.priority == Task.Priority.HIGH
    assert task.assigned_to == member

    assert task.project == project
    assert task.created_by == owner

@pytest.mark.django_db
def test_unassigned_team_member_cannot_update_task():
    owner = User.objects.create_user(
        username="owner_unassigned_member_task",
        email="owner_unassigned_member_task@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="unassigned_member_task",
        email="unassigned_member_task@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo tarea member no asignado",
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
        name="Proyecto tarea protegida",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea protegida",
        status=Task.Status.TODO,
        priority=Task.Priority.MEDIUM,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=member)

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
            "status": Task.Status.IN_PROGRESS,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    task.refresh_from_db()

    assert task.status == Task.Status.TODO
    assert task.priority == Task.Priority.MEDIUM

@pytest.mark.django_db
def test_assigned_team_member_can_update_task_status():
    owner = User.objects.create_user(
        username="owner_assigned_member_status",
        email="owner_assigned_member_status@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="assigned_member_status",
        email="assigned_member_status@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo cambio estado asignado",
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
        name="Proyecto estado asignado",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea asignada",
        description="El miembro puede cambiar su estado.",
        status=Task.Status.TODO,
        priority=Task.Priority.HIGH,
        assigned_to=member,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=member)

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
            "status": Task.Status.IN_PROGRESS,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["status"] == Task.Status.IN_PROGRESS
    assert response.data["assigned_to"] == member.pk
    assert response.data["priority"] == Task.Priority.HIGH

    task.refresh_from_db()

    assert task.status == Task.Status.IN_PROGRESS
    assert task.assigned_to == member
    assert task.priority == Task.Priority.HIGH

    