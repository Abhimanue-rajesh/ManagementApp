from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import localdate
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display

from tasks.models import (
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

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display_links = None
    list_display = (
        "name",
        "department",
        "project_type",
        "project_manager",
        "status",
        "deadline",
        "edit_project",
        "project_row_data",
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
        js = ("js/project_admin_row_click.js",)

    @admin.display(description="Action")
    def edit_project(self, obj):
        url = reverse(
            "admin:tasks_project_change",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}" '
            'onclick="event.stopPropagation();" '
            'class="inline-flex items-center justify-center '
            "font-medium rounded-default "
            "px-3 py-2 text-sm "
            "bg-transparent "
            "border border-base-300 "
            "text-base-700 "
            "hover:bg-primary-600 "
            "hover:border-primary-600 "
            "hover:text-white "
            "dark:border-base-700 "
            "dark:text-base-200 "
            "dark:hover:bg-primary-500 "
            "dark:hover:border-primary-500 "
            "dark:hover:text-white "
            'transition-colors">'
            "Edit Project"
            "</a>",
            url,
        )

    @admin.display(description="")
    def project_row_data(self, obj):
        return format_html(
            "<span "
            'class="project-row-data" '
            'data-project-id="{}" '
            'style="display:none;">'
            "</span>",
            obj.pk,
        )

    def response_change(self, request, obj):
        return redirect(
            f"{reverse('admin:tasks_task_changelist')}" f"?project__id__exact={obj.pk}"
        )

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
    change_form_template = "tasks/task_change_form.html"
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

        # Get selected project first
        selected_project = None

        if project_id:
            selected_project = (
                Project.objects.prefetch_related("team_members")
                .select_related(
                    "department",
                    "project_manager",
                )
                .filter(pk=project_id)
                .first()
            )
        project_days_remaining = None
        project_days_remaining_abs = None

        if selected_project and selected_project.deadline:
            today = timezone.localdate()

            project_days_remaining = (selected_project.deadline - today).days

            project_days_remaining_abs = abs(project_days_remaining)

        if request.method == "POST" and request.POST.get("_quick_add_task") == "1":
            title = request.POST.get("title")
            priority = request.POST.get("priority")
            due_date = request.POST.get("due_date") or localdate()
            status = request.POST.get("status") or "not_started"
            category_id = request.POST.get("category")

            selected_project_id = request.POST.get("project") or project_id

            if not title or not priority or not due_date:
                messages.error(
                    request,
                    "Please fill all required fields.",
                )
                return redirect(request.get_full_path())

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

            messages.success(
                request,
                "Task added successfully.",
            )

            return redirect(request.get_full_path())

        extra_context = extra_context or {}

        extra_context.update(
            {
                "task_categories": TaskCategory.objects.all(),
                "task_priorities": Task.PRIORITY,
                "task_statuses": Task.STATUS,
                "today": localdate(),
                "selected_project_id": project_id,
                "selected_project": selected_project,
                "project_days_remaining": project_days_remaining,
                "project_days_remaining_abs": project_days_remaining_abs,
            }
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

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

        if (
            request.resolver_match.url_name
            == f"{self.opts.app_label}_{self.opts.model_name}_changelist"
        ):
            if "status__exact" in request.GET:
                return queryset
            return queryset.exclude(status="closed")
        return queryset

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))

        if request.GET.get("project__id__exact") and "project" in list_display:
            list_display.remove("project")

        return tuple(list_display)

    def change_view(
        self,
        request,
        object_id,
        form_url="",
        extra_context=None,
    ):
        task = self.get_object(request, object_id)

        extra_context = extra_context or {}

        if task and task.project_id:
            extra_context["project_url"] = (
                f"{reverse('admin:tasks_task_changelist')}?project__id__exact={task.project_id}"
            )
            extra_context["project_button_text"] = "View Project"
        else:
            extra_context["project_url"] = reverse("admin:tasks_project_changelist")
            extra_context["project_button_text"] = "All Projects"

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


@admin.register(TaskCategory)
class TaskCategoryAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


User = get_user_model()
