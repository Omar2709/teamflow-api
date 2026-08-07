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

