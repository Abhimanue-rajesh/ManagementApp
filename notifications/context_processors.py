from notifications.models import Notification


def notification_status(request):
    has_unread_notifications = False

    if request.user.is_authenticated:
        has_unread_notifications = Notification.objects.filter(
            is_read=False,
        ).exists()

    return {"has_unread_notifications": has_unread_notifications}
