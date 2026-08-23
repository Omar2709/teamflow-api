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