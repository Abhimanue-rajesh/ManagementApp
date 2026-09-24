from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect
from django.utils.timezone import localdate
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from tasks.models import (
    Brand,
    PendingWith,
    Priority,
    ShortTaskReminder,
    Task,
    TaskActivity,
    TaskCategory,
    TaskEmail,
)


class TaskActivityAdmin(TabularInline):
    model = TaskActivity
    extra = 0
    fields = ("activity_note", "activity_date")
    ordering = ("-activity_date", "-pk")
    per_page = 2

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == "activity_note" and formfield:
            formfield.widget.attrs.update(
                {
                    "rows": 3,
                    "style": (
                        "width: 100%; max-width: none; "
                        "height: 4.5rem; min-height: 4.5rem; "
                        "resize: vertical;"
                    ),
                }
            )

        return formfield


class TaskEmailInline(TabularInline):
    model = TaskEmail
    extra = 0

    fields = (
        "subject",
        "sent_at",
    )
    readonly_fields = ("sent_at",)

    show_change_link = True


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    change_list_template = "tasks/change_list.html"

    list_display = (
        "title",
        "priority_badge",
        "status",
        "last_activity_date_display",
        "due_date",
        "pending_with",
    )

    list_filter = (
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
        TaskEmailInline,
    ]

    ordering = (
        "priority__sort_order",
        "due_date",
    )

    fieldsets = (
        (
            "Task Details",
            {
                "fields": (
                    (
                        "title",
                        "status",
                    ),
                    "description",
                    (
                        "category",
                        "pending_with",
                        "priority",
                    ),
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    ("created_at", "updated_date"),
                    ("due_date", "days_left"),
                    (
                        "is_overdue",
                        "deadline",
                    ),
                )
            },
        ),
    )

    class Media:
        js = (
            "js/task_autosave.js",
            "js/admin_row_click.js",
        )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == "description" and formfield:
            formfield.widget.attrs.update(
                {
                    "rows": 3,
                    "style": (
                        "width: 100%; max-width: none; "
                        "height: 5.5rem; min-height: 4.5rem; "
                        "resize: vertical;"
                    ),
                }
            )

        return formfield

    @display(
        description="Priority",
        label={
            "Critical": "danger",
            "High": "warning",
            "Medium": "info",
            "Low": "success",
        },
    )
    def priority_badge(self, obj):
        if not obj.priority:
            return "-"

        return obj.priority.name

    @admin.display(description="Last Activity")
    def last_activity_display(self, obj):
        activity = obj.last_activity()

        if not activity:
            return "-"

        return activity.activity_note

    @admin.display(description="Last Activity Date")
    def last_activity_date_display(self, obj):
        return obj.last_activity_date() or "-"

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and request.POST.get("_quick_add_task") == "1":
            title = request.POST.get("title")
            priority_id = request.POST.get("priority")
            due_date = request.POST.get("due_date") or localdate()
            status = request.POST.get("status") or "not_started"
            category_id = request.POST.get("category")

            if not title or not priority_id or not due_date:
                messages.error(
                    request,
                    "Please fill all required fields.",
                )
                return redirect(request.get_full_path())

            task = Task(
                title=title,
                priority_id=priority_id,
                due_date=due_date,
                status=status,
            )

            if category_id:
                task.category_id = category_id

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
                "task_priorities": Priority.objects.all(),
                "task_statuses": Task.STATUS,
                "today": localdate(),
            }
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        changelist_url_name = f"{self.opts.app_label}_{self.opts.model_name}_changelist"

        is_task_list = (
            request.resolver_match
            and request.resolver_match.url_name == changelist_url_name
        )
        is_searching = bool(request.GET.get("q", "").strip())

        if is_task_list and not is_searching:
            return queryset.exclude(status="closed")

        return queryset


@admin.register(TaskCategory)
class TaskCategoryAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


User = get_user_model()


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(Priority)
class PriorityAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(PendingWith)
class PendingWithAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(TaskEmail)
class TaskEmailAdmin(ModelAdmin):
    list_display = (
        "subject",
        "task",
        "sent_at",
    )

    list_filter = ("sent_at",)

    search_fields = (
        "subject",
        "task__title",
    )

    autocomplete_fields = ("task",)

    ordering = ("-sent_at",)

    fieldsets = (
        (
            "Email Details",
            {
                "fields": (
                    "task",
                    "subject",
                ),
            },
        ),
        (
            "Dates",
            {
                "fields": (("sent_at",),),
            },
        ),
    )

    @admin.display(description="Reminders")
    def reminder_count(self, obj):
        return obj.reminders.count()


@admin.register(ShortTaskReminder)
class ShortTaskReminderAdmin(ModelAdmin):
    change_list_template = "tasks/short_task_reminder/change_list.html"

    list_display = ("title", "is_done", "completed_at", "created_at")
    list_editable = ("is_done",)
    list_filter = ("is_done", "created_at")
    search_fields = ("title",)
    readonly_fields = ("completed_at", "created_at")
    ordering = ("is_done", "-created_at")
    list_per_page = 25

    fieldsets = (
        ("Task", {"fields": ("title", "is_done")}),
        ("Dates", {"fields": ("completed_at", "created_at")}),
    )

    def changelist_view(self, request, extra_context=None):
        if (
            request.method == "POST"
            and request.POST.get("_quick_add_short_task") == "1"
        ):
            if not self.has_add_permission(request):
                raise PermissionDenied

            reminder = ShortTaskReminder(
                title=request.POST.get("title", "").strip(),
            )

            try:
                reminder.full_clean()
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)
            else:
                reminder.save()
                messages.success(request, "Short task added successfully.")

            return redirect(request.get_full_path())

        extra_context = extra_context or {}
        extra_context["can_quick_add"] = self.has_add_permission(request)

        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        js = ("js/admin_row_click.js",)
