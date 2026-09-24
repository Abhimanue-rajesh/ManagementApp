from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TicketRouting(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Ticket Routings"

    def __str__(self):
        return self.name


class TicketStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ticket Status"
        verbose_name_plural = "Ticket Statuses"

    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    ticket_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )
    expected_deadline = models.DateField(
        null=True,
        blank=True,
    )
    ticket_name = models.CharField(max_length=255)
    routing = models.ForeignKey(
        TicketRouting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    last_updated_date = models.DateField(
        null=True,
        blank=True,
    )
    status_note = models.TextField(blank=True)
    raised_by = models.CharField(
        max_length=100,
        blank=True,
    )
    quote_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )
    related_ticket = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_tickets",
    )
    is_urgent = models.BooleanField(default=False)
    marked_for_review = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = [
            "-last_updated_date",
            "-ticket_number",
        ]
        verbose_name_plural = "Support Tickets"

    def clean(self):
        super().clean()

        if self.ticket_number:
            qs = SupportTicket.objects.filter(ticket_number=self.ticket_number)

            # Ignore the current object when editing
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    {"ticket_number": "This ticket number already exists."}
                )

    def __str__(self):
        if self.ticket_number:
            return f"{self.ticket_number} - {self.ticket_name}"
        return self.ticket_name

    def mark_updated(self):
        self.last_updated_date = timezone.localdate()
        self.save()

    def save(self, *args, **kwargs):
        self.last_updated_date = timezone.localdate()
        self.full_clean()
        super().save(*args, **kwargs)

    def days_since_update(self):
        if not self.last_updated_date:
            return None

        return (timezone.localdate() - self.last_updated_date).days

    def needs_update(self):
        days = self.days_since_update()

        return days is not None and days > 2


class SupportTicketHistory(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="histories",
    )
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Ticket History"
        verbose_name_plural = "Ticket Histories"

    def __str__(self):
        return f"{self.ticket} - {self.field_name}"
