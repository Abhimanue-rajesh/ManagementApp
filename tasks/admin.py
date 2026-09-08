from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.timezone import localdate
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display

from tasks.models import (
    Brand,
    PendingWith,
    Priority,
    Task,
    TaskActivity,
    TaskCategory,
    TaskEmail,
)


class TaskActivityAdmin(StackedInline):
    model = TaskActivity
    extra = 0


class TaskEmailInline(TabularInline):
    model = TaskEmail
    extra = 0

    fields = (
        "subject",
        "sent_at",
    )

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
