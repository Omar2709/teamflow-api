import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


@pytest.mark.django_db
def test_user_can_register():
    client = APIClient()

    payload = {
        "username": "usuario_test",
        "email": "usuario_test@example.com",
        "first_name": "Usuario",
        "last_name": "Test",
        "password": "Password123!",
        "password_confirmation": "Password123!",
    }

    response = client.post(
        reverse("users:register"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["username"] == payload["username"]
    assert response.data["email"] == payload["email"]
    assert response.data["first_name"] == payload["first_name"]
    assert response.data["last_name"] == payload["last_name"]

    assert "password" not in response.data
    assert "password_confirmation" not in response.data

    user = User.objects.get(username=payload["username"])

    assert user.check_password(payload["password"])


@pytest.mark.django_db
def test_registration_rejects_mismatched_passwords():
    client = APIClient()

    payload = {
        "username": "usuario_invalido",
        "email": "usuario_invalido@example.com",
        "first_name": "Usuario",
        "last_name": "Inválido",
        "password": "Password123!",
        "password_confirmation": "OtraPassword123!",
    }

    response = client.post(
        reverse("users:register"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "password_confirmation" in response.data

    assert not User.objects.filter(
        username=payload["username"],
    ).exists()


@pytest.mark.django_db
def test_registration_rejects_duplicate_username():
    User.objects.create_user(
        username="usuario_existente",
        email="primero@example.com",
        password="Password123!",
    )

    client = APIClient()

    payload = {
        "username": "usuario_existente",
        "email": "segundo@example.com",
        "first_name": "Segundo",
        "last_name": "Usuario",
        "password": "Password123!",
        "password_confirmation": "Password123!",
    }

    response = client.post(
        reverse("users:register"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data

    assert User.objects.filter(
        username="usuario_existente",
    ).count() == 1

@pytest.mark.django_db
def test_user_can_login_and_receive_jwt_tokens():
    password = "Password123!"

    User.objects.create_user(
        username="usuario_login",
        email="usuario_login@example.com",
        password=password,
    )

    client = APIClient()

    payload = {
        "username": "usuario_login",
        "password": password,
    }

    response = client.post(
        reverse("users:token-obtain-pair"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert "access" in response.data
    assert "refresh" in response.data

    assert isinstance(response.data["access"], str)
    assert isinstance(response.data["refresh"], str)

    assert len(response.data["access"]) > 0
    assert len(response.data["refresh"]) > 0

@pytest.mark.django_db
def test_login_rejects_invalid_password():
    User.objects.create_user(
        username="usuario_login_invalido",
        email="login_invalido@example.com",
        password="Password123!",
    )

    client = APIClient()

    payload = {
        "username": "usuario_login_invalido",
        "password": "PasswordIncorrecto123!",
    }

    response = client.post(
        reverse("users:token-obtain-pair"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert "access" not in response.data
    assert "refresh" not in response.data

def test_me_endpoint_rejects_unauthenticated_user():
    client = APIClient()

    response = client.get(
        reverse("users:me"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_authenticated_user_can_access_me_endpoint():
    user = User.objects.create_user(
        username="usuario_me",
        email="usuario_me@example.com",
        first_name="Usuario",
        last_name="Autenticado",
        password="Password123!",
    )

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    response = client.get(
        reverse("users:me"),
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["message"] == "Usuario autenticado."

    assert response.data["data"]["id"] == user.id
    assert response.data["data"]["username"] == user.username
    assert response.data["data"]["email"] == user.email
    assert response.data["data"]["first_name"] == user.first_name
    assert response.data["data"]["last_name"] == user.last_name

    assert "password" not in response.data["data"]

def test_me_endpoint_rejects_invalid_access_token():
    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION="Bearer token-invalido",
    )

    response = client.get(
        reverse("users:me"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data

@pytest.mark.django_db
def test_user_can_refresh_jwt_tokens():
    user = User.objects.create_user(
        username="usuario_refresh",
        email="usuario_refresh@example.com",
        password="Password123!",
    )

    original_refresh = RefreshToken.for_user(user)
    original_refresh_string = str(original_refresh)

    client = APIClient()

    response = client.post(
        reverse("users:token-refresh"),
        {
            "refresh": original_refresh_string,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert "access" in response.data
    assert "refresh" in response.data

    assert isinstance(response.data["access"], str)
    assert isinstance(response.data["refresh"], str)

    assert len(response.data["access"]) > 0
    assert len(response.data["refresh"]) > 0

    assert response.data["refresh"] != original_refresh_string

@pytest.mark.django_db
def test_old_refresh_token_is_blacklisted_after_rotation():
    user = User.objects.create_user(
        username="usuario_blacklist",
        email="usuario_blacklist@example.com",
        password="Password123!",
    )

    original_refresh = str(
        RefreshToken.for_user(user)
    )

    client = APIClient()

    first_response = client.post(
        reverse("users:token-refresh"),
        {
            "refresh": original_refresh,
        },
        format="json",
    )

    assert first_response.status_code == status.HTTP_200_OK
    assert "access" in first_response.data
    assert "refresh" in first_response.data

    second_response = client.post(
        reverse("users:token-refresh"),
        {
            "refresh": original_refresh,
        },
        format="json",
    )

    assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in second_response.data
    assert second_response.data["code"] == "token_not_valid"

@pytest.mark.django_db
def test_logout_blacklists_refresh_token():
    user = User.objects.create_user(
        username="usuario_logout",
        email="usuario_logout@example.com",
        password="Password123!",
    )

    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    refresh_token_string = str(refresh_token)

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    logout_response = client.post(
        reverse("users:logout"),
        {
            "refresh": refresh_token_string,
        },
        format="json",
    )

    assert logout_response.status_code == status.HTTP_200_OK
    assert (
        logout_response.data["message"]
        == "Sesión cerrada correctamente."
    )

    refresh_response = client.post(
        reverse("users:token-refresh"),
        {
            "refresh": refresh_token_string,
        },
        format="json",
    )

    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert refresh_response.data["code"] == "token_not_valid"

@pytest.mark.django_db
def test_logout_rejects_request_without_refresh_token():
    user = User.objects.create_user(
        username="usuario_logout_sin_refresh",
        email="logout_sin_refresh@example.com",
        password="Password123!",
    )

    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    response = client.post(
        reverse("users:logout"),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["message"]
        == "Debes proporcionar el refresh token."
    )

def test_logout_rejects_unauthenticated_user():
    client = APIClient()

    response = client.post(
        reverse("users:logout"),
        {
            "refresh": "token-cualquiera",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_logout_rejects_invalid_refresh_token():
    user = User.objects.create_user(
        username="usuario_logout_token_invalido",
        email="logout_token_invalido@example.com",
        password="Password123!",
    )

    valid_refresh = RefreshToken.for_user(user)
    access_token = str(valid_refresh.access_token)

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    response = client.post(
        reverse("users:logout"),
        {
            "refresh": "refresh-token-invalido",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["message"]
        == "El refresh token no es válido o ya fue invalidado."
    )

@pytest.mark.django_db
def test_token_verify_accepts_valid_access_token():
    user = User.objects.create_user(
        username="usuario_verify",
        email="usuario_verify@example.com",
        password="Password123!",
    )

    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)

    client = APIClient()

    response = client.post(
        reverse("users:token-verify"),
        {
            "token": access_token,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert not response.data

def test_token_verify_rejects_invalid_token():
    client = APIClient()

    response = client.post(
        reverse("users:token-verify"),
        {
            "token": "token-invalido",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data