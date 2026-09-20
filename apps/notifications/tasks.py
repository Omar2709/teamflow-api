import logging

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.db import InterfaceError, OperationalError

from .services import (
    create_due_soon_notifications,
)


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="notifications.notify_due_soon_tasks",
    autoretry_for=(
        OperationalError,
        InterfaceError,
    ),
    retry_backoff=5,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
    soft_time_limit=120,
    time_limit=150,
)
def notify_due_soon_tasks(self) -> int:
    logger.info(
        "Starting due-soon notification task. "
        "retry=%s",
        self.request.retries,
    )

    try:
        notifications = (
            create_due_soon_notifications()
        )

    except (
        OperationalError,
        InterfaceError,
    ):
        logger.exception(
            "Transient database failure while "
            "creating due-soon notifications. "
            "retry=%s",
            self.request.retries,
        )
        raise

    except SoftTimeLimitExceeded:
        logger.exception(
            "Due-soon notification task exceeded "
            "its soft time limit."
        )
        raise

    created_count = len(
        notifications
    )

    logger.info(
        "Due-soon notification task completed. "
        "created=%s retry=%s",
        created_count,
        self.request.retries,
    )

    return created_count