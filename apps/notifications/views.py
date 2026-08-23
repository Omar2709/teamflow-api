from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(
    generics.ListAPIView
):
    serializer_class = NotificationSerializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return (
            Notification.objects
            .filter(
                user=self.request.user,
            )
            .select_related("task")
            .order_by("-created_at")
        )


class NotificationMarkReadView(
    generics.GenericAPIView
):
    serializer_class = NotificationSerializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return (
            Notification.objects
            .filter(
                user=self.request.user,
            )
            .select_related("task")
        )

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()

            notification.save(
                update_fields=(
                    "is_read",
                    "read_at",
                )
            )

        serializer = self.get_serializer(
            notification,
        )

        return Response(serializer.data)