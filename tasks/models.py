from django.db import models
from django.utils import timezone
from django.utils.timezone import localdate


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class TaskCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Task Category"
        verbose_name_plural = "Task Categories"


class PendingWith(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Task Pending With"
        verbose_name_plural = "Task Pending With"


class Priority(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"


class Task(models.Model):
    STATUS = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("terminated", "Terminated"),
        ("waiting_for_approval", "Waiting For Approval"),
        ("closed", "Closed"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=27, choices=STATUS, default="not_started")
    priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pending_with = models.ForeignKey(
        PendingWith,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_tasks",
    )
    category = models.ForeignKey(
        TaskCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_date = models.DateField(auto_now=True)
    due_date = models.DateField(
        null=True,
        blank=True,
    )
    submitted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title

    def days_left(self):
        if not self.due_date:
            return None

        today = timezone.localdate()

        due_date = self.due_date

        # convert datetime to date if needed
        if hasattr(due_date, "date"):
            due_date = due_date.date()

        return (due_date - today).days

    # Helper: get next pending step in the action plan
    def next_action_step(self):
        return (
            self.action_steps.filter(status__in=["pending", "in_progress"])
            .order_by("order", "due_date")
            .first()
        )

    # Helper: check if there are any open steps
    def has_open_action_steps(self):
        return self.action_steps.exclude(status="closed").exists()

    def is_overdue(self):
        days = self.days_left()
        return days is not None and days < 0

    def deadline(self):
        """
        Human-friendly text for the email.
        """
        days = self.days_left()
        if days is None:
            return "No due date set"
        if days < 0:
            return f"Overdue by {abs(days)} day(s)"
        if days == 0:
            return "Due today"
        if days == 1:
            return "Due in 1 day"
        return f"Due in {days} days"

    def last_activity(self):
        return self.activities.order_by("-activity_date", "-created_at").first()

    def last_activity_date(self):
        activity = self.last_activity()
        return activity.activity_date if activity else None

    def days_since_last_activity(self):
        last_date = self.last_activity_date()

        if not last_date:
            return None

        return (timezone.localdate() - last_date).days

    def needs_activity_update(self):
        days = self.days_since_last_activity()
        return days is not None and days > 2


class TaskActionStep(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("completed", "Completed"),
    ]
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="action_steps",
    )
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )
    assigned_to = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order", "due_date", "id"]

    def __str__(self):
        return f"{self.task.title} - {self.title}"

    def mark_completed(self):
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()


class TaskActivity(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_note = models.TextField()
    activity_date = models.DateField(default=localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]
        verbose_name = "Task Activity"
        verbose_name_plural = "Task Activities"

    def __str__(self):
        return f"{self.task.title} - {self.activity_note}"


class TaskEmail(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="emails",
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
    )
    sent_at = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.subject or f"Email #{self.pk}"


class TaskEmailReminder(models.Model):
    email = models.ForeignKey(
        TaskEmail,
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    reminder_date = models.DateTimeField()
    note = models.TextField(
        blank=True,
    )
    sent = models.BooleanField(
        default=False,
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Reminder for {self.email} - {self.reminder_date}"

    class Meta:
        ordering = ("-reminder_date",)
