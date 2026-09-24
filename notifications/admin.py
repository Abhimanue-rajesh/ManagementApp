from django.contrib import admin
from unfold.admin import ModelAdmin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = (
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Notification",
            {
                "fields": (
                    "notification_type",
                    "title",
                    "message",
                    "link",
                )
            },
        ),
        (
            "Status",
            {
                "fields": ("is_read", "created_at"),
            },
        ),
    )

    class Media:
        js = ("js/admin_row_click.js",)
