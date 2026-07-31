from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse
from easyaudit.admin import CRUDEventAdmin as BaseCRUDEventAdmin
from easyaudit.admin import LoginEventAdmin as BaseLoginEventAdmin
from easyaudit.admin import RequestEventAdmin as BaseRequestEventAdmin
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent
from unfold.admin import ModelAdmin


def group_members_dashboard(request):
    groups = Group.objects.prefetch_related("user_set").order_by("name")

    context = {
        **admin.site.each_context(request),
        "title": "Group Members",
        "groups": groups,
    }

    return TemplateResponse(
        request,
        "admin/auth/group/group_members_dashboard.html",
        context,
    )


def safe_unregister(model):
    """
    Unregister a model only when it has already been registered.

    This avoids AlreadyRegistered and NotRegistered errors during
    development and testing.
    """
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


safe_unregister(CRUDEvent)
safe_unregister(LoginEvent)
safe_unregister(RequestEvent)


@admin.register(CRUDEvent)
class CRUDEventUnfoldAdmin(ModelAdmin, BaseCRUDEventAdmin):
    """
    Model create, update and delete audit events.
    """

    list_per_page = 50
    list_filter_sheet = True
    list_fullwidth = True
    compressed_fields = True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow opening the detail page but prevent editing.
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)

        return tuple(fields)


@admin.register(LoginEvent)
class LoginEventUnfoldAdmin(ModelAdmin, BaseLoginEventAdmin):
    """
    Login, logout and failed-login events.
    """

    list_per_page = 50
    list_filter_sheet = True
    list_fullwidth = True
    compressed_fields = True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RequestEvent)
class RequestEventUnfoldAdmin(ModelAdmin, BaseRequestEventAdmin):
    """
    HTTP request audit events.
    """

    list_per_page = 100
    list_filter_sheet = True
    list_fullwidth = True
    compressed_fields = True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False
