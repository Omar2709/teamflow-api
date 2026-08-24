from celery import shared_task

from .services import (
    create_due_soon_notifications,
)


@shared_task(
    name="notifications.notify_due_soon_tasks"
)
def notify_due_soon_tasks() -> int:
    notifications = (
        create_due_soon_notifications()
    )

    return len(notifications)