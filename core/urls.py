from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from dashboard.admin import group_members_dashboard
from dashboard.views import currency_converter, time_checker

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("lumen/", include("django_lumen.urls")),
    path(
        "admin/group-members/",
        admin.site.admin_view(group_members_dashboard),
        name="group_members_dashboard",
    ),
    path(
        "admin/time-checker/",
        admin.site.admin_view(time_checker),
        name="time_checker",
    ),
    path(
        "admin/currency-converter/",
        admin.site.admin_view(currency_converter),
        name="currency_converter",
    ),
    path(
        "", admin.site.urls
    ),  # this should be placed last as admin checks only the admin urls above this.
]
