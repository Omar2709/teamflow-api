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

@pytest.mark.django_db
def test_assigned_team_member_cannot_update_restricted_task_fields():
    owner = User.objects.create_user(
        username="owner_restricted_task_fields",
        email="owner_restricted_task_fields@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="assigned_member_restricted_fields",
        email="assigned_member_restricted_fields@example.com",
        password="Password123!",
    )

    other_member = User.objects.create_user(
        username="other_member_restricted_fields",
        email="other_member_restricted_fields@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo campos restringidos tarea",
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

    Membership.objects.create(
        team=team,
        user=other_member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto campos restringidos",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea con campos protegidos",
        status=Task.Status.TODO,
        priority=Task.Priority.MEDIUM,
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
            "priority": Task.Priority.HIGH,
            "assigned_to": other_member.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    task.refresh_from_db()

    assert task.priority == Task.Priority.MEDIUM
    assert task.assigned_to == member
    assert task.status == Task.Status.TODO

@pytest.mark.django_db
def test_task_cannot_be_assigned_to_user_outside_team():
    owner = User.objects.create_user(
        username="owner_invalid_task_assignment",
        email="owner_invalid_task_assignment@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_invalid_task_assignment",
        email="outsider_invalid_task_assignment@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo asignación protegida",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto asignación protegida",
        created_by=owner,
    )

    task = Task.objects.create(
        project=project,
        title="Tarea sin asignar",
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
            "assigned_to": outsider.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "assigned_to" in response.data

    task.refresh_from_db()

    assert task.assigned_to is None

@pytest.mark.django_db
def test_team_owner_and_admin_can_delete_tasks():
    owner = User.objects.create_user(
        username="owner_delete_tasks",
        email="owner_delete_tasks@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_delete_tasks",
        email="admin_delete_tasks@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo eliminación tareas",
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
        name="Proyecto eliminación tareas",
        created_by=owner,
    )

    owner_task = Task.objects.create(
        project=project,
        title="Tarea eliminable por owner",
        created_by=owner,
    )

    admin_task = Task.objects.create(
        project=project,
        title="Tarea eliminable por admin",
        created_by=owner,
    )

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)

    owner_response = owner_client.delete(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": owner_task.pk,
            },
        )
    )

    assert owner_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(
        pk=owner_task.pk,
    ).exists()

    assert Task.objects.filter(
        pk=admin_task.pk,
    ).exists()

    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)

    admin_response = admin_client.delete(
        reverse(
            "tasks:task-detail",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
                "pk": admin_task.pk,
            },
        )
    )

    assert admin_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(
        pk=admin_task.pk,
    ).exists()

@pytest.mark.django_db
def test_project_tasks_can_be_filtered_by_status():
    owner = User.objects.create_user(
        username="owner_filter_tasks_status",
        email="owner_filter_tasks_status@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo filtro estado tareas",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto filtro estado",
        created_by=owner,
    )

    todo_task = Task.objects.create(
        project=project,
        title="Tarea pendiente",
        status=Task.Status.TODO,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea en progreso",
        status=Task.Status.IN_PROGRESS,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea completada",
        status=Task.Status.DONE,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "status": Task.Status.TODO,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == 1

    assert response.data[0]["id"] == todo_task.pk
    assert response.data[0]["title"] == "Tarea pendiente"
    assert response.data[0]["status"] == Task.Status.TODO

@pytest.mark.django_db
def test_project_tasks_can_be_filtered_by_priority():
    owner = User.objects.create_user(
        username="owner_filter_tasks_priority",
        email="owner_filter_tasks_priority@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo filtro prioridad",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto filtro prioridad",
        created_by=owner,
    )

    high_priority_task = Task.objects.create(
        project=project,
        title="Tarea prioridad alta",
        priority=Task.Priority.HIGH,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea prioridad media",
        priority=Task.Priority.MEDIUM,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea prioridad baja",
        priority=Task.Priority.LOW,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "priority": Task.Priority.HIGH,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == high_priority_task.pk
    assert response.data[0]["priority"] == Task.Priority.HIGH

@pytest.mark.django_db
def test_project_tasks_can_be_filtered_by_assigned_user():
    owner = User.objects.create_user(
        username="owner_filter_assigned_tasks",
        email="owner_filter_assigned_tasks@example.com",
        password="Password123!",
    )

    first_member = User.objects.create_user(
        username="first_member_filter_tasks",
        email="first_member_filter_tasks@example.com",
        password="Password123!",
    )

    second_member = User.objects.create_user(
        username="second_member_filter_tasks",
        email="second_member_filter_tasks@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo filtro asignación",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=first_member,
        role=Membership.Role.MEMBER,
    )

    Membership.objects.create(
        team=team,
        user=second_member,
        role=Membership.Role.MEMBER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto filtro asignación",
        created_by=owner,
    )

    first_member_task = Task.objects.create(
        project=project,
        title="Tarea del primer miembro",
        assigned_to=first_member,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea del segundo miembro",
        assigned_to=second_member,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea sin asignar",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "assigned_to": first_member.pk,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == first_member_task.pk
    assert response.data[0]["assigned_to"] == first_member.pk

@pytest.mark.django_db
def test_project_tasks_can_be_filtered_by_status_and_priority():
    owner = User.objects.create_user(
        username="owner_combined_task_filters",
        email="owner_combined_task_filters@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo filtros combinados",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto filtros combinados",
        created_by=owner,
    )

    matching_task = Task.objects.create(
        project=project,
        title="Pendiente y urgente",
        status=Task.Status.TODO,
        priority=Task.Priority.HIGH,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Pendiente normal",
        status=Task.Status.TODO,
        priority=Task.Priority.MEDIUM,
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Urgente completada",
        status=Task.Status.DONE,
        priority=Task.Priority.HIGH,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "status": Task.Status.TODO,
            "priority": Task.Priority.HIGH,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == matching_task.pk
    assert response.data[0]["status"] == Task.Status.TODO
    assert response.data[0]["priority"] == Task.Priority.HIGH

@pytest.mark.django_db
def test_project_task_filter_rejects_invalid_status():
    owner = User.objects.create_user(
        username="owner_invalid_status_filter",
        email="owner_invalid_status_filter@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo filtro estado inválido",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto filtro inválido",
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Tarea existente",
        status=Task.Status.TODO,
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "status": "cancelled",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "status" in response.data

@pytest.mark.django_db
def test_project_tasks_can_be_searched_by_title():
    owner = User.objects.create_user(
        username="owner_search_task_title",
        email="owner_search_task_title@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo búsqueda título",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto búsqueda título",
        created_by=owner,
    )

    matching_task = Task.objects.create(
        project=project,
        title="Implementar autenticación JWT",
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Diseñar dashboard",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "search": "autenticación",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == matching_task.pk

@pytest.mark.django_db
def test_project_tasks_can_be_searched_by_description():
    owner = User.objects.create_user(
        username="owner_search_task_description",
        email="owner_search_task_description@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo búsqueda descripción",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto búsqueda descripción",
        created_by=owner,
    )

    matching_task = Task.objects.create(
        project=project,
        title="Configurar servidor",
        description="Preparar despliegue utilizando Docker.",
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Crear documentación",
        description="Documentar endpoints REST.",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "search": "Docker",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == matching_task.pk

@pytest.mark.django_db
def test_project_task_search_is_partial_and_case_insensitive():
    owner = User.objects.create_user(
        username="owner_partial_task_search",
        email="owner_partial_task_search@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo búsqueda parcial",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto búsqueda parcial",
        created_by=owner,
    )

    matching_task = Task.objects.create(
        project=project,
        title="Configurar PostgreSQL",
        created_by=owner,
    )

    Task.objects.create(
        project=project,
        title="Configurar Redis",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "search": "postgres",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == matching_task.pk

@pytest.mark.django_db
def test_project_tasks_can_be_ordered_by_due_date():
    owner = User.objects.create_user(
        username="owner_order_tasks_due_date",
        email="owner_order_tasks_due_date@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo orden fecha límite",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto orden fecha límite",
        created_by=owner,
    )

    last_task = Task.objects.create(
        project=project,
        title="Tarea para septiembre",
        due_date="2026-09-10",
        created_by=owner,
    )

    first_task = Task.objects.create(
        project=project,
        title="Tarea más próxima",
        due_date="2026-08-25",
        created_by=owner,
    )

    middle_task = Task.objects.create(
        project=project,
        title="Tarea intermedia",
        due_date="2026-09-01",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "ordering": "due_date",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = [
        task["id"]
        for task in response.data
    ]

    assert returned_ids == [
        first_task.pk,
        middle_task.pk,
        last_task.pk,
    ]

@pytest.mark.django_db
def test_project_tasks_can_be_ordered_by_created_at_descending():
    owner = User.objects.create_user(
        username="owner_order_tasks_created",
        email="owner_order_tasks_created@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo orden creación",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    project = Project.objects.create(
        team=team,
        name="Proyecto orden creación",
        created_by=owner,
    )

    first_task = Task.objects.create(
        project=project,
        title="Primera tarea creada",
        created_by=owner,
    )

    second_task = Task.objects.create(
        project=project,
        title="Segunda tarea creada",
        created_by=owner,
    )

    third_task = Task.objects.create(
        project=project,
        title="Tercera tarea creada",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "tasks:project-task-list-create",
            kwargs={
                "team_id": team.pk,
                "project_id": project.pk,
            },
        ),
        {
            "ordering": "-created_at",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = [
        task["id"]
        for task in response.data
    ]

    assert returned_ids == [
        third_task.pk,
        second_task.pk,
        first_task.pk,
    ]

