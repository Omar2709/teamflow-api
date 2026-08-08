import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Membership, Team


User = get_user_model()


@pytest.mark.django_db
def test_authenticated_user_can_create_team():
    user = User.objects.create_user(
        username="creador_equipo",
        email="creador@example.com",
        password="Password123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "name": "   Equipo    Backend   ",
        "description": "Equipo para practicar Django REST Framework.",
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["name"] == "Equipo Backend"
    assert response.data["description"] == payload["description"]
    assert response.data["created_by"]["id"] == user.id
    assert response.data["member_count"] == 1

    team = Team.objects.get(id=response.data["id"])

    assert team.created_by == user

    membership = Membership.objects.get(
        team=team,
        user=user,
    )

    assert membership.role == Membership.Role.OWNER

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_team():
    client = APIClient()

    payload = {
        "name": "Equipo no autorizado",
        "description": "Este equipo no debe crearse.",
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Team.objects.count() == 0
    assert Membership.objects.count() == 0

@pytest.mark.django_db
def test_user_only_lists_teams_where_is_member():
    user = User.objects.create_user(
        username="usuario_equipos",
        email="usuario_equipos@example.com",
        password="Password123!",
    )

    other_user = User.objects.create_user(
        username="otro_usuario",
        email="otro_usuario@example.com",
        password="Password123!",
    )

    own_team = Team.objects.create(
        name="Equipo visible",
        description="El usuario pertenece a este equipo.",
        created_by=user,
    )

    Membership.objects.create(
        team=own_team,
        user=user,
        role=Membership.Role.OWNER,
    )

    other_team = Team.objects.create(
        name="Equipo privado",
        description="Pertenece a otro usuario.",
        created_by=other_user,
    )

    Membership.objects.create(
        team=other_team,
        user=other_user,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        reverse("teams:team-list-create"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    assert response.data[0]["id"] == own_team.id
    assert response.data[0]["name"] == "Equipo visible"

    returned_ids = {
        team["id"]
        for team in response.data
    }

    assert other_team.id not in returned_ids

@pytest.mark.django_db
def test_user_can_list_team_created_by_another_user_when_is_member():
    owner = User.objects.create_user(
        username="propietario_equipo",
        email="propietario@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="miembro_equipo",
        email="miembro@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo compartido",
        description="Equipo creado por otra persona.",
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

    response = client.get(
        reverse("teams:team-list-create"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    returned_team = response.data[0]

    assert returned_team["id"] == team.id
    assert returned_team["name"] == "Equipo compartido"
    assert returned_team["created_by"]["id"] == owner.id
    assert returned_team["member_count"] == 2

def test_unauthenticated_user_cannot_list_teams():
    client = APIClient()

    response = client.get(
        reverse("teams:team-list-create"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_team_creation_rejects_name_with_only_spaces():
    user = User.objects.create_user(
        username="usuario_nombre_invalido",
        email="nombre_invalido@example.com",
        password="Password123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "name": "       ",
        "description": "Este equipo no debe crearse.",
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    assert Team.objects.count() == 0
    assert Membership.objects.count() == 0

@pytest.mark.django_db
def test_team_creation_rejects_name_longer_than_120_characters():
    user = User.objects.create_user(
        username="usuario_nombre_largo",
        email="nombre_largo@example.com",
        password="Password123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "name": "a" * 121,
        "description": "Este equipo no debe crearse.",
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    assert Team.objects.count() == 0
    assert Membership.objects.count() == 0

@pytest.mark.django_db
def test_authenticated_user_can_create_team_without_description():
    user = User.objects.create_user(
        username="usuario_sin_descripcion",
        email="sin_descripcion@example.com",
        password="Password123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "name": "Equipo sin descripción",
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["name"] == payload["name"]
    assert response.data["description"] == ""
    assert response.data["created_by"]["id"] == user.id
    assert response.data["member_count"] == 1

    team = Team.objects.get(id=response.data["id"])

    assert team.description == ""

    membership = Membership.objects.get(
        team=team,
        user=user,
    )

    assert membership.role == Membership.Role.OWNER

@pytest.mark.django_db
def test_team_creation_ignores_server_controlled_fields():
    authenticated_user = User.objects.create_user(
        username="creador_real",
        email="creador_real@example.com",
        password="Password123!",
    )

    other_user = User.objects.create_user(
        username="creador_falso",
        email="creador_falso@example.com",
        password="Password123!",
    )

    client = APIClient()
    client.force_authenticate(user=authenticated_user)

    payload = {
        "name": "Equipo seguro",
        "description": "Prueba de campos protegidos.",
        "created_by": {
            "id": other_user.id,
        },
        "member_count": 999,
    }

    response = client.post(
        reverse("teams:team-list-create"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert (
        response.data["created_by"]["id"]
        == authenticated_user.id
    )
    assert response.data["member_count"] == 1

    team = Team.objects.get(id=response.data["id"])

    assert team.created_by == authenticated_user
    assert team.created_by != other_user

    assert Membership.objects.filter(
        team=team,
        user=authenticated_user,
        role=Membership.Role.OWNER,
    ).exists()

    assert not Membership.objects.filter(
        team=team,
        user=other_user,
    ).exists()

@pytest.mark.django_db
def test_team_member_can_retrieve_team_detail():
    owner = User.objects.create_user(
        username="propietario_detalle",
        email="propietario_detalle@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo consultable",
        description="Equipo para probar el endpoint de detalle.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == team.id
    assert response.data["name"] == team.name
    assert response.data["description"] == team.description
    assert response.data["created_by"]["id"] == owner.id
    assert response.data["member_count"] == 1

@pytest.mark.django_db
def test_user_cannot_retrieve_team_where_is_not_member():
    owner = User.objects.create_user(
        username="propietario_equipo_privado",
        email="propietario_privado@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="usuario_externo",
        email="usuario_externo@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo privado",
        description="Equipo visible únicamente para sus miembros.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.get(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data

@pytest.mark.django_db
def test_team_owner_can_update_team():
    owner = User.objects.create_user(
        username="propietario_actualizacion",
        email="propietario_actualizacion@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre anterior",
        description="Descripción anterior.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    payload = {
        "name": "   Equipo    actualizado   ",
        "description": "Descripción actualizada.",
    }

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["name"] == "Equipo actualizado"
    assert response.data["description"] == "Descripción actualizada."
    assert response.data["created_by"]["id"] == owner.id
    assert response.data["member_count"] == 1

    team.refresh_from_db()

    assert team.name == "Equipo actualizado"
    assert team.description == "Descripción actualizada."
    assert team.created_by == owner

@pytest.mark.django_db
def test_team_admin_can_update_team():
    owner = User.objects.create_user(
        username="propietario_equipo_admin",
        email="propietario_equipo_admin@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="administrador_equipo",
        email="administrador_equipo@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo administrado",
        description="Descripción original.",
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

    payload = {
        "name": "Equipo actualizado por admin",
        "description": "Descripción modificada por el administrador.",
    }

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["name"] == payload["name"]
    assert response.data["description"] == payload["description"]
    assert response.data["created_by"]["id"] == owner.id
    assert response.data["member_count"] == 2

    team.refresh_from_db()

    assert team.name == payload["name"]
    assert team.description == payload["description"]
    assert team.created_by == owner

@pytest.mark.django_db
def test_team_member_cannot_update_team():
    owner = User.objects.create_user(
        username="propietario_equipo_restringido",
        email="propietario_restringido@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="miembro_sin_permiso",
        email="miembro_sin_permiso@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre original",
        description="Descripción original.",
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

    payload = {
        "name": "Nombre que no debe guardarse",
        "description": "Cambio no autorizado.",
    }

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    team.refresh_from_db()

    assert team.name == "Nombre original"
    assert team.description == "Descripción original."
    assert team.created_by == owner

def test_unauthenticated_user_cannot_retrieve_team_detail():
    client = APIClient()

    response = client.get(
        reverse(
            "teams:team-detail",
            kwargs={"pk": 1},
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthenticated_user_cannot_update_team():
    client = APIClient()

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": 1},
        ),
        {
            "name": "Intento no autorizado",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_outsider_cannot_update_team():
    owner = User.objects.create_user(
        username="owner_equipo_privado_update",
        email="owner_privado_update@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_update",
        email="outsider_update@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo privado",
        description="Descripción original.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "Intento externo",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    team.refresh_from_db()

    assert team.name == "Equipo privado"
    assert team.description == "Descripción original."

@pytest.mark.django_db
def test_team_owner_can_update_only_name():
    owner = User.objects.create_user(
        username="owner_patch_name",
        email="owner_patch_name@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre original",
        description="Descripción que debe conservarse.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "   Nuevo    nombre   ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Nuevo nombre"
    assert (
        response.data["description"]
        == "Descripción que debe conservarse."
    )

    team.refresh_from_db()

    assert team.name == "Nuevo nombre"
    assert team.description == "Descripción que debe conservarse."

@pytest.mark.django_db
def test_team_owner_can_update_only_description():
    owner = User.objects.create_user(
        username="owner_patch_description",
        email="owner_patch_description@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre que debe conservarse",
        description="Descripción original.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "description": "Nueva descripción.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Nombre que debe conservarse"
    assert response.data["description"] == "Nueva descripción."

    team.refresh_from_db()

    assert team.name == "Nombre que debe conservarse"
    assert team.description == "Nueva descripción."

@pytest.mark.django_db
def test_team_update_rejects_name_with_only_spaces():
    owner = User.objects.create_user(
        username="owner_update_blank",
        email="owner_update_blank@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre válido",
        description="Descripción original.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "       ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    team.refresh_from_db()

    assert team.name == "Nombre válido"

@pytest.mark.django_db
def test_team_update_rejects_name_longer_than_120_characters():
    owner = User.objects.create_user(
        username="owner_update_long_name",
        email="owner_update_long_name@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Nombre original",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "a" * 121,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    team.refresh_from_db()

    assert team.name == "Nombre original"

@pytest.mark.django_db
def test_team_update_ignores_created_by():
    owner = User.objects.create_user(
        username="owner_protected_creator",
        email="owner_protected_creator@example.com",
        password="Password123!",
    )

    other_user = User.objects.create_user(
        username="fake_creator_update",
        email="fake_creator_update@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo seguro",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "Equipo actualizado",
            "created_by": {
                "id": other_user.id,
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["created_by"]["id"] == owner.id

    team.refresh_from_db()

    assert team.created_by == owner
    assert team.created_by != other_user

@pytest.mark.django_db
def test_team_update_ignores_member_count():
    owner = User.objects.create_user(
        username="owner_protected_member_count",
        email="owner_member_count@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo conteo",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "member_count": 999,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["member_count"] == 1

    assert team.memberships.count() == 1

@pytest.mark.django_db
def test_team_detail_rejects_put_method():
    owner = User.objects.create_user(
        username="owner_put_disabled",
        email="owner_put_disabled@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo PUT",
        description="Descripción original.",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.put(
        reverse(
            "teams:team-detail",
            kwargs={"pk": team.pk},
        ),
        {
            "name": "Intento con PUT",
            "description": "No debería actualizarse.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    team.refresh_from_db()

    assert team.name == "Equipo PUT"
    assert team.description == "Descripción original."

@pytest.mark.django_db
def test_team_owner_can_list_members():
    owner = User.objects.create_user(
        username="owner_list_members",
        email="owner_list_members@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_list_members",
        email="member_list_members@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo con miembros",
        description="Equipo para probar el listado de miembros.",
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
    client.force_authenticate(user=owner)

    response = client.get(
        reverse(
            "teams:team-members",
            kwargs={"team_id": team.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    members_by_username = {
        item["username"]: item
        for item in response.data
    }

    assert "owner_list_members" in members_by_username
    assert "member_list_members" in members_by_username

    owner_data = members_by_username["owner_list_members"]

    assert owner_data["id"] == owner.id
    assert owner_data["email"] == owner.email
    assert owner_data["role"] == Membership.Role.OWNER
    assert "joined_at" in owner_data

    member_data = members_by_username["member_list_members"]

    assert member_data["id"] == member.id
    assert member_data["email"] == member.email
    assert member_data["role"] == Membership.Role.MEMBER
    assert "joined_at" in member_data

@pytest.mark.django_db
def test_team_admin_can_list_members():
    owner = User.objects.create_user(
        username="owner_admin_list_members",
        email="owner_admin_list_members@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_list_members",
        email="admin_list_members@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo listado por admin",
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

    response = client.get(
        reverse(
            "teams:team-members",
            kwargs={"team_id": team.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    returned_usernames = {
        item["username"]
        for item in response.data
    }

    assert owner.username in returned_usernames
    assert admin.username in returned_usernames

@pytest.mark.django_db
def test_team_member_can_list_members():
    owner = User.objects.create_user(
        username="owner_member_list",
        email="owner_member_list@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="normal_member_list",
        email="normal_member_list@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo listado por miembro",
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

    response = client.get(
        reverse(
            "teams:team-members",
            kwargs={"team_id": team.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    returned_usernames = {
        item["username"]
        for item in response.data
    }

    assert owner.username in returned_usernames
    assert member.username in returned_usernames

@pytest.mark.django_db
def test_outsider_cannot_list_team_members():
    owner = User.objects.create_user(
        username="owner_private_members",
        email="owner_private_members@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_members",
        email="outsider_members@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo miembros privados",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.get(
        reverse(
            "teams:team-members",
            kwargs={"team_id": team.id},
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data

def test_unauthenticated_user_cannot_list_team_members():
    client = APIClient()

    response = client.get(
        reverse(
            "teams:team-members",
            kwargs={"team_id": 1},
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_team_owner_can_add_member():
    owner = User.objects.create_user(
        username="owner_add_member",
        email="owner_add_member@example.com",
        password="Password123!",
    )

    new_member = User.objects.create_user(
        username="new_team_member",
        email="new_team_member@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo para agregar miembros",
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
            "teams:team-members",
            kwargs={"team_id": team.id},
        ),
        {
            "username": new_member.username,
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["id"] == new_member.id
    assert response.data["username"] == new_member.username
    assert response.data["email"] == new_member.email
    assert response.data["role"] == Membership.Role.MEMBER
    assert "joined_at" in response.data

    membership = Membership.objects.get(
        team=team,
        user=new_member,
    )

    assert membership.role == Membership.Role.MEMBER

    assert team.memberships.count() == 2

@pytest.mark.django_db
def test_team_admin_can_add_member():
    owner = User.objects.create_user(
        username="owner_admin_add_member",
        email="owner_admin_add_member@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_add_member",
        email="admin_add_member@example.com",
        password="Password123!",
    )

    new_member = User.objects.create_user(
        username="member_added_by_admin",
        email="member_added_by_admin@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo administrado",
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
            "teams:team-members",
            kwargs={"team_id": team.id},
        ),
        {
            "username": new_member.username,
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["id"] == new_member.id
    assert response.data["username"] == new_member.username
    assert response.data["email"] == new_member.email
    assert response.data["role"] == Membership.Role.MEMBER
    assert "joined_at" in response.data

    membership = Membership.objects.get(
        team=team,
        user=new_member,
    )

    assert membership.role == Membership.Role.MEMBER

    assert team.memberships.count() == 3

@pytest.mark.django_db
def test_team_member_cannot_add_member():
    owner = User.objects.create_user(
        username="owner_member_cannot_add",
        email="owner_member_cannot_add@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_without_add_permission",
        email="member_without_add_permission@example.com",
        password="Password123!",
    )

    new_user = User.objects.create_user(
        username="user_not_added",
        email="user_not_added@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo restringido",
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
            "teams:team-members",
            kwargs={"team_id": team.id},
        ),
        {
            "username": new_user.username,
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert not Membership.objects.filter(
        team=team,
        user=new_user,
    ).exists()

    assert team.memberships.count() == 2

@pytest.mark.django_db
def test_cannot_add_same_user_twice_to_team():
    owner = User.objects.create_user(
        username="owner_duplicate_member",
        email="owner_duplicate_member@example.com",
        password="Password123!",
    )

    existing_member = User.objects.create_user(
        username="existing_team_member",
        email="existing_team_member@example.com",
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
        user=existing_member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "teams:team-members",
            kwargs={"team_id": team.id},
        ),
        {
            "username": existing_member.username,
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data

    assert (
        Membership.objects.filter(
            team=team,
            user=existing_member,
        ).count()
        == 1
    )

    assert team.memberships.count() == 2

@pytest.mark.django_db
def test_cannot_add_nonexistent_user_to_team():
    owner = User.objects.create_user(
        username="owner_nonexistent_user",
        email="owner_nonexistent_user@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo usuario inexistente",
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
            "teams:team-members",
            kwargs={"team_id": team.id},
        ),
        {
            "username": "usuario_que_no_existe",
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data

    assert Membership.objects.filter(
        team=team,
    ).count() == 1

    assert team.memberships.count() == 1

@pytest.mark.django_db
def test_team_owner_can_promote_member_to_admin():
    owner = User.objects.create_user(
        username="owner_promote_member",
        email="owner_promote_member@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_to_promote",
        email="member_to_promote@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo promoción",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": member.id,
            },
        ),
        {
            "role": Membership.Role.ADMIN,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == member.id
    assert response.data["username"] == member.username
    assert response.data["role"] == Membership.Role.ADMIN

    membership.refresh_from_db()

    assert membership.role == Membership.Role.ADMIN

@pytest.mark.django_db
def test_team_owner_can_demote_admin_to_member():
    owner = User.objects.create_user(
        username="owner_demote_admin",
        email="owner_demote_admin@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_to_demote",
        email="admin_to_demote@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo degradación",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    membership = Membership.objects.create(
        team=team,
        user=admin,
        role=Membership.Role.ADMIN,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": admin.id,
            },
        ),
        {
            "role": Membership.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == admin.id
    assert response.data["username"] == admin.username
    assert response.data["role"] == Membership.Role.MEMBER

    membership.refresh_from_db()

    assert membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_team_admin_cannot_change_member_role():
    owner = User.objects.create_user(
        username="owner_admin_cannot_change_role",
        email="owner_admin_cannot_change_role@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_cannot_change_role",
        email="admin_cannot_change_role@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_target_by_admin",
        email="member_target_by_admin@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo roles restringidos admin",
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

    member_membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": member.id,
            },
        ),
        {
            "role": Membership.Role.ADMIN,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    member_membership.refresh_from_db()

    assert member_membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_team_member_cannot_change_roles():
    owner = User.objects.create_user(
        username="owner_member_cannot_change_role",
        email="owner_member_cannot_change_role@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_cannot_change_role",
        email="member_cannot_change_role@example.com",
        password="Password123!",
    )

    other_member = User.objects.create_user(
        username="other_member_role_target",
        email="other_member_role_target@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo roles restringidos member",
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

    target_membership = Membership.objects.create(
        team=team,
        user=other_member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.patch(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": other_member.id,
            },
        ),
        {
            "role": Membership.Role.ADMIN,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    target_membership.refresh_from_db()

    assert target_membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_team_owner_cannot_assign_owner_role_through_role_endpoint():
    owner = User.objects.create_user(
        username="current_team_owner",
        email="current_team_owner@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_cannot_become_owner",
        email="member_cannot_become_owner@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo propiedad protegida",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    member_membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": member.id,
            },
        ),
        {
            "role": Membership.Role.OWNER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "role" in response.data

    member_membership.refresh_from_db()

    assert member_membership.role == Membership.Role.MEMBER

    assert Membership.objects.filter(
        team=team,
        role=Membership.Role.OWNER,
    ).count() == 1

    assert Membership.objects.filter(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    ).exists()

@pytest.mark.django_db
def test_team_owner_can_remove_member():
    owner = User.objects.create_user(
        username="owner_remove_member",
        email="owner_remove_member@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_to_remove",
        email="member_to_remove@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo eliminación member",
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
    client.force_authenticate(user=owner)

    response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": member.id,
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Membership.objects.filter(
        team=team,
        user=member,
    ).exists()

    assert Membership.objects.filter(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    ).exists()

    assert team.memberships.count() == 1

@pytest.mark.django_db
def test_team_owner_can_remove_admin():
    owner = User.objects.create_user(
        username="owner_remove_admin",
        email="owner_remove_admin@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_to_remove",
        email="admin_to_remove@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo eliminación admin",
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
    client.force_authenticate(user=owner)

    response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": admin.id,
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Membership.objects.filter(
        team=team,
        user=admin,
    ).exists()

    assert team.memberships.count() == 1

@pytest.mark.django_db
def test_team_admin_can_remove_member():
    owner = User.objects.create_user(
        username="owner_admin_remove_member",
        email="owner_admin_remove_member@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_remove_member",
        email="admin_remove_member@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_removed_by_admin",
        email="member_removed_by_admin@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo admin elimina member",
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

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": member.id,
            },
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Membership.objects.filter(
        team=team,
        user=member,
    ).exists()

    assert Membership.objects.filter(
        team=team,
        user=admin,
        role=Membership.Role.ADMIN,
    ).exists()

    assert team.memberships.count() == 2

@pytest.mark.django_db
def test_team_admin_cannot_remove_owner_or_admin():
    owner = User.objects.create_user(
        username="protected_owner",
        email="protected_owner@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="requesting_admin",
        email="requesting_admin@example.com",
        password="Password123!",
    )

    other_admin = User.objects.create_user(
        username="protected_admin",
        email="protected_admin@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo roles protegidos",
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
        user=other_admin,
        role=Membership.Role.ADMIN,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    owner_response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": owner.id,
            },
        )
    )

    assert owner_response.status_code == status.HTTP_403_FORBIDDEN

    admin_response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": other_admin.id,
            },
        )
    )

    assert admin_response.status_code == status.HTTP_403_FORBIDDEN

    assert Membership.objects.filter(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    ).exists()

    assert Membership.objects.filter(
        team=team,
        user=other_admin,
        role=Membership.Role.ADMIN,
    ).exists()

    assert team.memberships.count() == 3

@pytest.mark.django_db
def test_team_owner_cannot_leave_team():
    owner = User.objects.create_user(
        username="owner_cannot_leave",
        email="owner_cannot_leave@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo que necesita propietario",
        created_by=owner,
    )

    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.delete(
        reverse(
            "teams:team-member-detail",
            kwargs={
                "team_id": team.id,
                "user_id": owner.id,
            },
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert Membership.objects.filter(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    ).exists()

    assert Membership.objects.filter(
        team=team,
        role=Membership.Role.OWNER,
    ).count() == 1

    assert team.memberships.count() == 1

@pytest.mark.django_db
def test_team_owner_can_transfer_ownership():
    owner = User.objects.create_user(
        username="current_owner_transfer",
        email="current_owner_transfer@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="new_owner_transfer",
        email="new_owner_transfer@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    member_membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={
                "team_id": team.id,
            },
        ),
        {
            "user_id": member.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert (
        response.data["message"]
        == "Propiedad transferida correctamente."
    )

    assert response.data["new_owner"]["id"] == member.id
    assert (
        response.data["new_owner"]["role"]
        == Membership.Role.OWNER
    )

    owner_membership.refresh_from_db()
    member_membership.refresh_from_db()
    team.refresh_from_db()

    assert owner_membership.role == Membership.Role.ADMIN
    assert member_membership.role == Membership.Role.OWNER

    assert Membership.objects.filter(
        team=team,
        role=Membership.Role.OWNER,
    ).count() == 1

    assert team.created_by == owner

@pytest.mark.django_db
def test_team_admin_cannot_transfer_ownership():
    owner = User.objects.create_user(
        username="owner_admin_transfer",
        email="owner_admin_transfer@example.com",
        password="Password123!",
    )

    admin = User.objects.create_user(
        username="admin_cannot_transfer",
        email="admin_cannot_transfer@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_transfer_target",
        email="member_transfer_target@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia restringida admin",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=admin,
        role=Membership.Role.ADMIN,
    )

    member_membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": team.id},
        ),
        {
            "user_id": member.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    owner_membership.refresh_from_db()
    member_membership.refresh_from_db()

    assert owner_membership.role == Membership.Role.OWNER
    assert member_membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_team_member_cannot_transfer_ownership():
    owner = User.objects.create_user(
        username="owner_member_transfer",
        email="owner_member_transfer@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="member_cannot_transfer",
        email="member_cannot_transfer@example.com",
        password="Password123!",
    )

    target = User.objects.create_user(
        username="member_transfer_second_target",
        email="member_transfer_second_target@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia restringida member",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    target_membership = Membership.objects.create(
        team=team,
        user=target,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": team.id},
        ),
        {
            "user_id": target.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    owner_membership.refresh_from_db()
    target_membership.refresh_from_db()

    assert owner_membership.role == Membership.Role.OWNER
    assert target_membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_outsider_cannot_transfer_team_ownership():
    owner = User.objects.create_user(
        username="owner_private_transfer",
        email="owner_private_transfer@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_transfer",
        email="outsider_transfer@example.com",
        password="Password123!",
    )

    member = User.objects.create_user(
        username="private_transfer_member",
        email="private_transfer_member@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia privada",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    member_membership = Membership.objects.create(
        team=team,
        user=member,
        role=Membership.Role.MEMBER,
    )

    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": team.id},
        ),
        {
            "user_id": member.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    owner_membership.refresh_from_db()
    member_membership.refresh_from_db()

    assert owner_membership.role == Membership.Role.OWNER
    assert member_membership.role == Membership.Role.MEMBER

@pytest.mark.django_db
def test_team_owner_cannot_transfer_ownership_to_outsider():
    owner = User.objects.create_user(
        username="owner_transfer_to_outsider",
        email="owner_transfer_to_outsider@example.com",
        password="Password123!",
    )

    outsider = User.objects.create_user(
        username="outsider_cannot_be_owner",
        email="outsider_cannot_be_owner@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia solo miembros",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": team.id},
        ),
        {
            "user_id": outsider.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    owner_membership.refresh_from_db()

    assert owner_membership.role == Membership.Role.OWNER

    assert not Membership.objects.filter(
        team=team,
        user=outsider,
    ).exists()

    assert Membership.objects.filter(
        team=team,
        role=Membership.Role.OWNER,
    ).count() == 1

@pytest.mark.django_db
def test_team_owner_cannot_transfer_ownership_to_self():
    owner = User.objects.create_user(
        username="owner_self_transfer",
        email="owner_self_transfer@example.com",
        password="Password123!",
    )

    team = Team.objects.create(
        name="Equipo transferencia propia",
        created_by=owner,
    )

    owner_membership = Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": team.id},
        ),
        {
            "user_id": owner.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "user_id" in response.data

    owner_membership.refresh_from_db()

    assert owner_membership.role == Membership.Role.OWNER

    assert Membership.objects.filter(
        team=team,
        role=Membership.Role.OWNER,
    ).count() == 1

def test_unauthenticated_user_cannot_transfer_team_ownership():
    client = APIClient()

    response = client.post(
        reverse(
            "teams:team-transfer-ownership",
            kwargs={"team_id": 1},
        ),
        {
            "user_id": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

