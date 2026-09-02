from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse


def health(_request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            "status": "ok",
        }
    )


def _database_is_ready() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return False

    return True


def readiness(_request: HttpRequest) -> JsonResponse:
    if not _database_is_ready():
        return JsonResponse(
            {
                "status": "unavailable",
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ready",
        }
    )