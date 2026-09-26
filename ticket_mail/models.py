from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone


class MailboxSyncState(models.Model):
    started_at = models.DateTimeField(default=timezone.now)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket mailbox active since {self.started_at}"


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    subject = models.CharField(max_length=255)
    requester_name = models.CharField(max_length=255, blank=True)
    requester_email = models.EmailField()
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_support_tickets",
    )
    received_at = models.DateTimeField(default=timezone.now)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def ticket_number(self):
        return f"IT-{self.pk:06d}" if self.pk else "IT-NEW"

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"


class TicketEmailMessage(models.Model):
    """Tracks incoming Gmail messages and prevents duplicate imports."""

    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="email_messages",
    )
    gmail_message_id = models.CharField(max_length=128, unique=True)
    gmail_thread_id = models.CharField(max_length=128, db_index=True)
    sender_email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    received_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["received_at"]

    def __str__(self):
        return f"{self.ticket.ticket_number}: {self.gmail_message_id}"


def attachment_path(instance, filename):
    extension = Path(filename).suffix.lower()[:20]
    return f"ticket_mail/{instance.ticket_id}/" f"{uuid4().hex}{extension}"


private_attachment_storage = FileSystemStorage(
    location=settings.TICKET_MAIL_PRIVATE_ROOT,
    base_url=None,
)


class AllowedEmailDomain(models.Model):
    domain = models.CharField(max_length=253, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("domain",)

    def save(self, *args, **kwargs):
        self.domain = self.domain.strip().lower().lstrip("@")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(
        "SupportTicket",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    message = models.ForeignKey(
        "TicketEmailMessage",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    part_index = models.PositiveIntegerField()
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    file = models.FileField(
        storage=private_attachment_storage,
        upload_to=attachment_path,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("message", "part_index"),
                name="unique_ticket_mail_attachment_part",
            )
        ]

    def __str__(self):
        return self.original_name
