from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.timezone import localdate
from django.views.generic import TemplateView
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin

from tasks.models import (
    Brand,
    DailyTask,
)

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
