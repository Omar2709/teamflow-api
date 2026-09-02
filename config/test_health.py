import pytest
from django.urls import reverse


def test_health_returns_ok(client):
    response = client.get(
        reverse("health")
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


@pytest.mark.django_db
def test_readiness_returns_ready_when_database_is_available(
    client,
):
    response = client.get(
        reverse("readiness")
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
    }


def test_readiness_returns_503_when_database_is_unavailable(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "config.health._database_is_ready",
        lambda: False,
    )

    response = client.get(
        reverse("readiness")
    )

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
    }