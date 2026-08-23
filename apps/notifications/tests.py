import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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

