import json

from dateutil.relativedelta import relativedelta
from django.contrib import admin

# from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import localdate

from subscriptions.models import SubscriptionTracker
from tasks.models import Task, TaskCategory
from tickets.models import SupportTicket
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

    # daily_tasks_queryset = DailyTask.objects.select_related(
    #     "user",
    #     "brand",
    #     "created_by",
    # )

    # if not request.user.is_superuser:
    #     daily_tasks_queryset = daily_tasks_queryset.filter(user=request.user)

    # today_daily_tasks = daily_tasks_queryset.filter(task_date=today).order_by(
    #     "-created_at"
    # )

    # daily_task_status_counts = {
    #     "total": today_daily_tasks.count(),
    #     "not_started": today_daily_tasks.filter(status="not_started").count(),
    #     "in_progress": today_daily_tasks.filter(status="in_progress").count(),
    #     "completed": today_daily_tasks.filter(status="completed").count(),
    #     "on_hold": today_daily_tasks.filter(status="on_hold").count(),
    # }

    today = localdate()
    start_month = today.replace(day=1) - relativedelta(months=4)

    monthly_data = (
        Task.objects.filter(created_at__gte=start_month)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            not_started=Count(
                "id",
                filter=Q(status="not_started"),
            ),
            in_progress=Count(
                "id",
                filter=Q(status="in_progress"),
            ),
            waiting_for_approval=Count(
                "id",
                filter=Q(status="waiting_for_approval"),
            ),
            closed=Count(
                "id",
                filter=Q(status="closed"),
            ),
            terminated=Count(
                "id",
                filter=Q(status="terminated"),
            ),
        )
        .order_by("month")
    )

    monthly_lookup = {item["month"].strftime("%Y-%m"): item for item in monthly_data}

    labels = []
    not_started_counts = []
    in_progress_counts = []
    waiting_counts = []
    closed_counts = []
    terminated_counts = []

    for index in range(5):
        month = start_month + relativedelta(months=index)
        month_key = month.strftime("%Y-%m")
        month_data = monthly_lookup.get(month_key, {})

        labels.append(month.strftime("%b %Y"))
        not_started_counts.append(month_data.get("not_started", 0))
        in_progress_counts.append(month_data.get("in_progress", 0))
        waiting_counts.append(month_data.get("waiting_for_approval", 0))
        closed_counts.append(month_data.get("closed", 0))
        terminated_counts.append(month_data.get("terminated", 0))

    task_summary = Task.objects.aggregate(
        total=Count("id"),
        not_started=Count(
            "id",
            filter=Q(status="not_started"),
        ),
        in_progress=Count(
            "id",
            filter=Q(status="in_progress"),
        ),
        waiting_for_approval=Count(
            "id",
            filter=Q(status="waiting_for_approval"),
        ),
        closed=Count(
            "id",
            filter=Q(status="closed"),
        ),
        terminated=Count(
            "id",
            filter=Q(status="terminated"),
        ),
    )

    # projects = Project.objects.annotate(
    #     total_tasks=Count("tasks"),
    #     not_started_tasks=Count(
    #         "tasks",
    #         filter=Q(tasks__status="not_started"),
    #     ),
    #     in_progress_tasks=Count(
    #         "tasks",
    #         filter=Q(tasks__status="in_progress"),
    #     ),
    #     waiting_for_approval_tasks=Count(
    #         "tasks",
    #         filter=Q(tasks__status="waiting_for_approval"),
    #     ),
    #     closed_tasks=Count(
    #         "tasks",
    #         filter=Q(tasks__status="closed"),
    #     ),
    #     terminated_tasks=Count(
    #         "tasks",
    #         filter=Q(tasks__status="terminated"),
    #     ),
    # ).order_by("name")

    upcoming_subscriptions = SubscriptionTracker.objects.filter(
        status="active",
        debit_date__gte=timezone.localdate(),
    ).order_by("debit_date")[:5]

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
            # "daily_task_status_counts": daily_task_status_counts,
            # "daily_task_changelist_url": reverse("admin:tasks_dailytask_changelist"),
            "task_summary": task_summary,
            # "projects": projects,
            "task_chart_labels": json.dumps(labels),
            "task_not_started_counts": json.dumps(not_started_counts),
            "task_in_progress_counts": json.dumps(in_progress_counts),
            "task_waiting_counts": json.dumps(waiting_counts),
            "task_closed_counts": json.dumps(closed_counts),
            "task_terminated_counts": json.dumps(terminated_counts),
            # "task_list_url": reverse("admin:tasks_task_changelist"),
            # "total_projects": Project.objects.count(),
            # "project_list_url": reverse("admin:tasks_project_changelist"),
            "upcoming_subscriptions": upcoming_subscriptions,
        }
    )

    return context


def time_checker(request):
    context = {
        **admin.site.each_context(request),
        "title": "Time Checker",
    }

    return render(
        request,
        "dashboard/time_checker.html",
        context,
    )


def currency_converter(request):
    context = {
        **admin.site.each_context(request),
        "title": "Currency Converter",
    }

    return render(
        request,
        "dashboard/currency_converter.html",
        context,
    )
