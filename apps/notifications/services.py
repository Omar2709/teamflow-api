from apps.tasks.models import Task
from apps.users.models import User

from .models import Notification


def create_task_assignment_notification(
    *,
    task: Task,
    actor: User,
    previous_assignee_id: int | None = None,
) -> Notification | None:
    assigned_user = task.assigned_to

    if assigned_user is None:
        return None

    if previous_assignee_id == assigned_user.pk:
        return None

    if assigned_user.pk == actor.pk:
        return None

    return Notification.objects.create(
        user=assigned_user,
        type=Notification.Type.TASK_ASSIGNED,
        message=f'Te asignaron la tarea "{task.title}".',
        task=task,
    )

def create_comment_notifications(
    *,
    comment,
    actor: User,
) -> list[Notification]:
    task = comment.task

    recipient_ids = {
        user_id
        for user_id in (
            task.assigned_to_id,
            task.created_by_id,
        )
        if (
            user_id is not None
            and user_id != actor.pk
        )
    }

    if not recipient_ids:
        return []

    notifications = [
        Notification(
            user_id=user_id,
            type=Notification.Type.COMMENT_CREATED,
            message=(
                f'{actor.username} comentó en la tarea '
                f'"{task.title}".'
            ),
            task=task,
        )
        for user_id in sorted(recipient_ids)
    ]

    return Notification.objects.bulk_create(
        notifications
    )