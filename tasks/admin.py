import json

from dateutil.relativedelta import relativedelta
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.timezone import localdate
from django.views.generic import TemplateView
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display
from unfold.views import UnfoldModelAdminViewMixin

from tasks.models import (
    Brand,
    DailyTask,
    Department,
    Project,
    ProjectHistory,
    ProjectType,
    Task,
    TaskActionStep,
    TaskActivity,
    TaskCategory,
)


class ProjectHistoryInline(TabularInline):
    model = ProjectHistory
    extra = 0
    fields = (
        "action",
        "previous_status",
        "new_status",
        "description",
        "updated_by",
        "created_at",
    )
    readonly_fields = (
        "updated_by",
        "created_at",
    )
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        "name",
        "department",
        "project_type",
        "project_manager",
        "status",
        "deadline",
        "updated_at",
    )

    list_filter = (
        "status",
        "department",
        "project_type",
        "deadline",
    )

    search_fields = (
        "name",
        "description",
        "project_manager__username",
        "team_members__username",
    )

    filter_horizontal = ("team_members",)

    readonly_fields = (
        "created_by",
        "created_at",
        "updated_at",
    )

    inlines = [
        ProjectHistoryInline,
    ]

    class Media:
        js = ("js/admin_row_click.js",)

    def save_model(self, request, obj, form, change):
        previous_status = None

        if change and obj.pk:
            previous_status = (
                Project.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )

        if not obj.pk:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

        if not change:
            ProjectHistory.objects.create(
                project=obj,
                action="created",
                new_status=obj.status,
                description="Project created.",
                updated_by=request.user,
            )

        elif previous_status != obj.status:
            ProjectHistory.objects.create(
                project=obj,
                action="status_changed",
                previous_status=previous_status or "",
                new_status=obj.status,
                description=(
                    f"Project status changed from "
                    f"{previous_status} to {obj.status}."
                ),
                updated_by=request.user,
            )


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )

    search_fields = ("name",)

    list_filter = ("is_active",)


@admin.register(ProjectType)
class ProjectTypeAdmin(ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )

    search_fields = ("name",)

    list_filter = ("is_active",)


@admin.register(ProjectHistory)
class ProjectHistoryAdmin(ModelAdmin):
    list_display = (
        "project",
        "action",
        "previous_status",
        "new_status",
        "updated_by",
        "created_at",
    )

    list_filter = (
        "action",
        "previous_status",
        "new_status",
        "created_at",
    )

    search_fields = (
        "project__name",
        "description",
        "updated_by__username",
    )

    readonly_fields = (
        "project",
        "action",
        "previous_status",
        "new_status",
        "description",
        "updated_by",
        "created_at",
    )

    def has_add_permission(self, request):
        return False


class TasksDashboard(UnfoldModelAdminViewMixin, TemplateView):
    title = "Task Dashboard"
    permission_required = ()
    template_name = "tasks/tasks_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        monthly_lookup = {
            item["month"].strftime("%Y-%m"): item for item in monthly_data
        }

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

        projects = Project.objects.annotate(
            total_tasks=Count("tasks"),
            not_started_tasks=Count(
                "tasks",
                filter=Q(tasks__status="not_started"),
            ),
            in_progress_tasks=Count(
                "tasks",
                filter=Q(tasks__status="in_progress"),
            ),
            waiting_for_approval_tasks=Count(
                "tasks",
                filter=Q(tasks__status="waiting_for_approval"),
            ),
            closed_tasks=Count(
                "tasks",
                filter=Q(tasks__status="closed"),
            ),
            terminated_tasks=Count(
                "tasks",
                filter=Q(tasks__status="terminated"),
            ),
        ).order_by("name")
        context.update(
            {
                # "projects": Project.objects.all().order_by("name"),
                "task_list_url": reverse("admin:tasks_task_changelist"),
                "task_chart_labels": json.dumps(labels),
                "task_not_started_counts": json.dumps(not_started_counts),
                "task_in_progress_counts": json.dumps(in_progress_counts),
                "task_waiting_counts": json.dumps(waiting_counts),
                "task_closed_counts": json.dumps(closed_counts),
                "task_terminated_counts": json.dumps(terminated_counts),
                "task_summary": task_summary,
                "projects": projects,
            }
        )

        return context


class TaskActionStepInline(StackedInline):
    model = TaskActionStep
    extra = 0
    fields = (
        "order",
        "title",
        "status",
        "due_date",
        "started_at",
        "completed_at",
    )


class TaskActivityAdmin(StackedInline):
    model = TaskActivity
    extra = 0


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    change_list_template = "tasks/change_list.html"
    list_display = (
        "project",
        "title",
        "priority",
        "status",
        "last_activity_date_display",
        "due_date",
        "pending_with",
    )
    list_filter = (
        "project",
        "status",
        "priority",
        "category",
        "due_date",
    )
    search_fields = (
        "title",
        "description",
    )
    list_editable = ("status",)
    autocomplete_fields = ("category",)
    readonly_fields = (
        "created_at",
        "updated_date",
        "submitted_date",
        "days_left",
        "is_overdue",
        "deadline",
    )
    inlines = [
        TaskActivityAdmin,
        TaskActionStepInline,
    ]
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Task Details",
            {
                "fields": (
                    "project",
                    "title",
                    "description",
                    "category",
                    "priority",
                    "status",
                    "pending_with",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    ("created_at", "updated_date"),
                    "due_date",
                    "days_left",
                    "is_overdue",
                    "deadline",
                )
            },
        ),
    )

    class Media:
        js = (
            "js/task_autosave.js",
            "js/admin_row_click.js",
        )

    @display(
        description="Priority",
        label={
            "critical": "danger",
            "high": "warning",
            "medium": "info",
            "low": "success",
        },
    )
    def priority_badge(self, obj):
        return obj.priority

    def changelist_view(self, request, extra_context=None):
        project_id = request.GET.get("project__id__exact")
        if request.method == "POST" and request.POST.get("_quick_add_task") == "1":
            title = request.POST.get("title")
            priority = request.POST.get("priority")
            due_date = request.POST.get("due_date") or localdate()
            status = request.POST.get("status") or "not_started"
            category_id = request.POST.get("category")
            selected_project_id = request.POST.get("project") or project_id
            if not title or not priority or not due_date:
                messages.error(request, "Please fill all required fields.")
                return redirect(request.path)

            task = Task(
                user=request.user,
                title=title,
                priority=priority,
                due_date=due_date,
                status=status,
            )
            if category_id:
                task.category_id = category_id

            if selected_project_id:
                task.project_id = selected_project_id

            task.save()

            messages.success(request, "Task added successfully.")
            return redirect(request.get_full_path())

        extra_context = extra_context or {}
        extra_context["task_categories"] = TaskCategory.objects.all()
        extra_context["task_priorities"] = Task.PRIORITY
        extra_context["task_statuses"] = Task.STATUS
        extra_context["today"] = localdate()
        extra_context["selected_project_id"] = project_id
        extra_context["selected_project"] = (
            Project.objects.get(id=project_id) if project_id else None
        )

        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user

        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse("admin:tasks_task_change", args=[obj.pk]))

    def response_change(self, request, obj):
        return redirect(reverse("admin:tasks_task_change", args=[obj.pk]))

    @admin.display(description="Last Activity")
    def last_activity_display(self, obj):
        activity = obj.last_activity()

        if not activity:
            return "-"

        return activity.activity_note

    @admin.display(description="Last Activity Date")
    def last_activity_date_display(self, obj):
        return obj.last_activity_date() or "-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # If status filter is selected, allow Django filter to work normally
        if "status__exact" in request.GET:
            return queryset

        # Default view: hide closed tasks
        return queryset.exclude(status="closed")

    def get_urls(self):
        custom_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(TasksDashboard.as_view(model_admin=self)),
                name="tasks_dashboard",
            ),
        ]

        return custom_urls + super().get_urls()

    # This is done so that when in filter the project title is not shown in the table
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))

        if request.GET.get("project__id__exact") and "project" in list_display:
            list_display.remove("project")

        return tuple(list_display)


@admin.register(TaskCategory)
class TaskCategoryAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


User = get_user_model()


class DailyTaskDashboard(UnfoldModelAdminViewMixin, TemplateView):
    title = "Daily Tasks"
    permission_required = ()
    template_name = "tasks/daily_task_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = localdate()

        users = (
            User.objects.filter(
                groups__name="Daily Task Workers",
                is_active=True,
            )
            .annotate(
                total_daily_tasks=Count(
                    "daily_tasks",
                    filter=Q(daily_tasks__task_date=today),
                    distinct=True,
                ),
                pending_approval_count=Count(
                    "daily_tasks",
                    filter=Q(
                        daily_tasks__approval_status="pending",
                        daily_tasks__task_date=today,
                    ),
                    distinct=True,
                ),
            )
            .distinct()
            .order_by("first_name", "username")
        )

        context.update(
            {
                "daily_task_users": users,
                "daily_task_list_url": reverse("admin:tasks_dailytask_changelist"),
                "today": today,
            }
        )

        return context


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(DailyTask)
class DailyTaskAdmin(ModelAdmin):
    change_list_template = "tasks/daily_task_change_list.html"

    list_display = (
        "title",
        "brand",
        "task_date",
        "created_by",
        "status",
        "approval_status",
    )

    list_filter = (
        "user",
        "task_date",
        "status",
        "approval_status",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = (
        "task_date",
        "created_by",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-task_date",
        "-created_at",
    )

    class Media:
        js = ("js/admin_row_click.js",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            return queryset

        if request.user.has_perm("tasks.view_all_dailytasks"):
            return queryset

        return queryset.filter(user=request.user)

    def get_urls(self):
        custom_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(
                    DailyTaskDashboard.as_view(model_admin=self)
                ),
                name="daily_task_dashboard",
            ),
            path(
                "quick-add/",
                self.admin_site.admin_view(self.quick_add_daily_task),
                name="tasks_dailytask_quick_add",
            ),
        ]

        return custom_urls + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        filtered_user_id = request.GET.get("user__id__exact")
        filtered_user = None

        if filtered_user_id:
            filtered_user = User.objects.filter(
                pk=filtered_user_id,
                is_active=True,
            ).first()
        extra_context.update(
            {
                "filtered_user": filtered_user,
                "filtered_user_id": filtered_user_id,
                "brands": Brand.objects.all().order_by("name"),
                "quick_add_url": reverse("admin:tasks_dailytask_quick_add"),
            }
        )
        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    def quick_add_daily_task(self, request):

        if request.method != "POST":
            return HttpResponseRedirect(reverse("admin:tasks_dailytask_changelist"))

        user_id = request.POST.get("user")
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        brand_id = request.POST.get("brand")
        status = request.POST.get("status", "not_started")
        redirect_url = reverse("admin:tasks_dailytask_changelist")

        if user_id:
            redirect_url = f"{redirect_url}?user__id__exact={user_id}"

        if not user_id:
            messages.error(request, "Please select a user.")
            return HttpResponseRedirect(redirect_url)

        if not title:
            messages.error(request, "Task title is required.")
            return HttpResponseRedirect(redirect_url)

        task_user = get_object_or_404(
            User,
            pk=user_id,
            is_active=True,
        )

        brand = None

        if brand_id:
            brand = Brand.objects.filter(pk=brand_id).first()

        valid_statuses = {value for value, label in DailyTask.STATUS}

        if status not in valid_statuses:
            status = "not_started"

        daily_task = DailyTask.objects.create(
            user=task_user,
            title=title,
            brand=brand,
            description=description,
            status=status,
            approval_status="pending",
            created_by=request.user,
        )

        messages.success(
            request,
            f'Daily task "{daily_task.title}" assigned successfully.',
        )

        return HttpResponseRedirect(redirect_url)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))

        if request.GET.get("user__id__exact"):
            if "user" in list_display:
                list_display.remove("user")

        return tuple(list_display)
