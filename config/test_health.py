import pytest

from django.db import DatabaseError
from django.test import override_settings
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

@pytest.mark.django_db
@override_settings(
    ALLOWED_HOSTS=[
        "api.teamflow.test",
    ],
    SECURE_SSL_REDIRECT=True,
    SECURE_REDIRECT_EXEMPT=[
        r"^health/$",
        r"^ready/$",
    ],
)
def test_readiness_accepts_alb_private_host(
    client,
):
    response = client.get(
        reverse("readiness"),
        HTTP_HOST="10.20.1.25:8000",
        HTTP_USER_AGENT=(
            "ELB-HealthChecker/2.0"
        ),
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
    }

@override_settings(
    ALLOWED_HOSTS=[
        "api.teamflow.test",
    ],
    SECURE_SSL_REDIRECT=False,
)
def test_regular_endpoint_rejects_invalid_host(
    client,
):
    response = client.get(
        reverse("schema"),
        HTTP_HOST="evil.example.com",
    )

    assert response.status_code == 400

@override_settings(
    ALLOWED_HOSTS=[
        "api.teamflow.test",
    ],
    SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=(
        "HTTP_X_FORWARDED_PROTO",
        "https",
    ),
)
def test_forwarded_https_is_treated_as_secure(
    client,
):
    response = client.get(
        reverse("schema"),
        HTTP_HOST="api.teamflow.test",
        HTTP_X_FORWARDED_PROTO="https",
        HTTP_ACCEPT=(
            "application/vnd.oai."
            "openapi+json"
        ),
    )

    assert response.status_code == 200

@override_settings(
    ALLOWED_HOSTS=[
        "api.teamflow.test",
    ],
    SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=(
        "HTTP_X_FORWARDED_PROTO",
        "https",
    ),
)
def test_regular_http_request_redirects_to_https(
    client,
):
    response = client.get(
        reverse("schema"),
        HTTP_HOST="api.teamflow.test",
    )

    assert response.status_code == 301

    assert response["Location"].startswith(
        "https://"
    )

def test_readiness_logs_database_failure(
    client,
    monkeypatch,
    caplog,
):
    def unavailable():
        raise DatabaseError(
            "database unavailable"
        )

    monkeypatch.setattr(
        "config.health.connection.cursor",
        unavailable,
    )

    with caplog.at_level(
        "ERROR",
        logger="config.health",
    ):
        response = client.get(
            reverse("readiness"),
        )

    assert response.status_code == 503

    assert (
        "Database readiness check failed."
        in caplog.text
    )