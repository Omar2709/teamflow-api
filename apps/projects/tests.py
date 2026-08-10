import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.teams.models import Membership, Team

from .models import Project


User = get_user_model()

@pytest.mark.django_db
def test_team_owner_can_create_project():
    owner = User.objects.create_user(
        username="owner_create_project",
        email="owner_create_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo proyectos owner",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "   API    Principal   ",
            "description": "Backend principal.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["name"] == "API Principal"
    assert response.data["description"] == "Backend principal."
    assert response.data["team"] == team.id
    assert response.data["created_by"]["id"] == owner.id

    project = Project.objects.get(
        id=response.data["id"],
    )

    assert project.team == team
    assert project.created_by == owner

@pytest.mark.django_db
def test_team_admin_can_create_project():
    owner = User.objects.create_user(
        username="owner_admin_project",
        email="owner_admin_project@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_create_project",
        email="admin_create_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo proyectos admin",
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

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "Proyecto del admin",
            "description": "Creado por administrador.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created_by"]["id"] == admin.id
    assert response.data["team"] == team.id

    assert Project.objects.filter(
        team=team,
        created_by=admin,
        name="Proyecto del admin",
    ).exists()

@pytest.mark.django_db
def test_team_member_cannot_create_project():
    owner = User.objects.create_user(
        username="owner_member_project",
        email="owner_member_project@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_cannot_create_project",
        email="member_cannot_create_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo proyecto restringido",
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

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "Proyecto no autorizado",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert Project.objects.count() == 0

@pytest.mark.django_db
def test_outsider_cannot_create_project():
    owner = User.objects.create_user(
        username="owner_private_project",
        email="owner_private_project@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_create_project",
        email="outsider_create_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo privado proyectos",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "Proyecto externo",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert Project.objects.count() == 0

def test_unauthenticated_user_cannot_create_project():
    client = APIClient()

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": 1},
        ),
        {
            "name": "Proyecto anónimo",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_team_member_can_list_projects():
    owner = User.objects.create_user(
        username="owner_list_projects",
        email="owner_list_projects@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_list_projects",
        email="member_list_projects@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo listado proyectos",
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

    first_project = Project.objects.create(
        team=team,
        name="Proyecto uno",
        created_by=owner,
    )

    second_project = Project.objects.create(
        team=team,
        name="Proyecto dos",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    returned_ids = {
        project["id"]
        for project in response.data
    }

    assert first_project.id in returned_ids
    assert second_project.id in returned_ids

@pytest.mark.django_db
def test_project_list_only_returns_projects_from_requested_team():
    user = User.objects.create_user(
        username="multi_team_project_user",
        email="multi_team_project_user@example.com",
        password="Password123!",
    )

    first_team = Team.objects.create(
        name="Primer equipo",
        created_by=user,
    )

    second_team = Team.objects.create(
        name="Segundo equipo",
        created_by=user,
    )

    Membership.objects.create(
        team=first_team,
        user=user,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=second_team,
        user=user,
        role=Membership.Role.OWNER,
    )

    first_project = Project.objects.create(
        team=first_team,
        name="Proyecto primer equipo",
        created_by=user,
    )

    second_project = Project.objects.create(
        team=second_team,
        name="Proyecto segundo equipo",
        created_by=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": first_team.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == first_project.id

    returned_ids = {
        project["id"]
        for project in response.data
    }

    assert second_project.id not in returned_ids

@pytest.mark.django_db
def test_project_creation_rejects_name_with_only_spaces():
    owner = User.objects.create_user(
        username="owner_blank_project",
        email="owner_blank_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo nombre vacío proyecto",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "        ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    assert Project.objects.count() == 0

@pytest.mark.django_db
def test_project_creation_rejects_name_longer_than_120_characters():
    owner = User.objects.create_user(
        username="owner_long_project",
        email="owner_long_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo nombre largo proyecto",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "a" * 121,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    assert Project.objects.count() == 0

@pytest.mark.django_db
def test_cannot_create_duplicate_project_name_in_same_team():
    owner = User.objects.create_user(
        username="owner_duplicate_project",
        email="owner_duplicate_project@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo proyectos únicos",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Project.objects.create(
        team=team,
        name="API interna",
        created_by=owner,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "projects:team-project-list-create",
            kwargs={"team_id": team.id},
        ),
        {
            "name": "   API    interna   ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    assert Project.objects.filter(
        team=team,
    ).count() == 1

