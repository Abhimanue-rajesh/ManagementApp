from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = "info", "Information"
        TICKET = "ticket", "Ticket"
        TASK = "task", "Task"
        SUBSCRIPTION = "subscription", "Subscription"
        DOMAIN = "domain", "Domain"
        APPROVAL = "approval", "Approval"

    title = models.CharField(max_length=255)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO,
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="Internal page path to open when clicked.",
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["is_read", "-created_at"],
            ),
        ]

    def __str__(self):
        return self.title
