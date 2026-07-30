from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from dashboard.admin import group_members_dashboard

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path(
        "admin/group-members/",
        admin.site.admin_view(group_members_dashboard),
        name="group_members_dashboard",
    ),
    path("", admin.site.urls),
]
