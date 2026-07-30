import json

from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.urls import reverse
from django.utils import timezone

from tasks.models import DailyTask, Task, TaskCategory
from tickets.models import SupportTicket, TicketStatus
from web_management.models import DomainManager, WebFormManager


def normalize_month(value):
    if not value:
        return None

    return value.replace(day=1)


def dashboard_callback(request, context):
    today = timezone.localdate()
    start_month = today.replace(day=1) - relativedelta(months=4)

    months = []
    current = start_month

    while current <= today:
        months.append(current)
        current += relativedelta(months=1)

    month_labels = [month.strftime("%b %Y") for month in months]

    created_data = (
        SupportTicket.objects.filter(created_at__gte=start_month)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    created_map = {
        normalize_month(item["month"]): item["count"] for item in created_data
    }

    created_counts = [created_map.get(month.replace(day=1), 0) for month in months]

    today = timezone.localdate()

    domain_renewal_reminders = [
        domain
        for domain in DomainManager.objects.select_related("registrar")
        if domain.needs_renewal_reminder()
    ]

    form_test_reminders = [
        form
        for form in WebFormManager.objects.select_related(
            "webpage",
            "webpage__domain",
        )
        if form.needs_testing()
    ]

    ticket_status_counts = TicketStatus.objects.annotate(
        ticket_count=Count("tickets")
    ).order_by("name")

    daily_tasks_queryset = DailyTask.objects.select_related(
        "user",
        "brand",
        "created_by",
    )

    if not request.user.is_superuser:
        daily_tasks_queryset = daily_tasks_queryset.filter(user=request.user)

    today_daily_tasks = daily_tasks_queryset.filter(task_date=today).order_by(
        "-created_at"
    )

    daily_task_status_counts = {
        "total": today_daily_tasks.count(),
        "not_started": today_daily_tasks.filter(status="not_started").count(),
        "in_progress": today_daily_tasks.filter(status="in_progress").count(),
        "completed": today_daily_tasks.filter(status="completed").count(),
        "on_hold": today_daily_tasks.filter(status="on_hold").count(),
    }
    context.update(
        {
            "ticket_chart_labels": json.dumps(month_labels),
            "ticket_created_counts": json.dumps(created_counts),
            "total_tickets": SupportTicket.objects.count(),
            "total_tasks": Task.objects.count(),
            "task_category_counts": TaskCategory.objects.annotate(
                task_count=Count("task")
            ).order_by("name"),
            "domain_renewal_reminders": domain_renewal_reminders,
            "domain_renewal_count": len(domain_renewal_reminders),
            "form_test_reminders": form_test_reminders,
            "form_test_count": len(form_test_reminders),
            "ticket_status_counts": ticket_status_counts,
            "daily_task_status_counts": daily_task_status_counts,
            "daily_task_changelist_url": reverse("admin:tasks_dailytask_changelist"),
        }
    )

    return context
