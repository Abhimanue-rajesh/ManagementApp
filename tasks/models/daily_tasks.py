from django.conf import settings
from django.db import models
from django.utils.timezone import localdate


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class DailyTask(models.Model):
    STATUS = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
    ]
    APPROVAL_STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    task_date = models.DateField(default=localdate)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_tasks",
    )
    title = models.CharField(max_length=200)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_tasks",
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="not_started",
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_daily_tasks",
        editable=False,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-task_date", "-created_at"]
        verbose_name = "Daily Task"
        verbose_name_plural = "Daily Tasks"

    def __str__(self):
        return f"{self.user} - {self.title}"
