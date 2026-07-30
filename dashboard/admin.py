from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse


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
