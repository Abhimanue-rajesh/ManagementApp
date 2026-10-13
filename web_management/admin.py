from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline

from web_management.forms import DNSZoneAdminForm
from web_management.models import (
    DNSZone,
    DomainManager,
    Registrar,
    WebFormManager,
    WebPageManager,
)


class WebPageInline(StackedInline):
    model = WebPageManager
    extra = 0


class WebFormInline(StackedInline):
    model = WebFormManager
    extra = 0


@admin.register(Registrar)
class RegistrarAdmin(ModelAdmin):
    list_display = (
        "name",
        "website",
    )
    search_fields = (
        "name",
        "website",
    )


@admin.register(DomainManager)
class DomainManagerAdmin(ModelAdmin):
    list_display = (
        "domain_name",
        "registrar",
        "expiry_date",
        "days_until_expiry",
        "renewal_status",
        "updated_at",
    )
    search_fields = (
        "domain_name",
        "registrar__name",
    )
    list_filter = ("renewal_status", "expiry_date")
    ordering = ("expiry_date",)
    inlines = [WebPageInline]

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(WebPageManager)
class WebPageManagerAdmin(ModelAdmin):
    list_display = (
        "page_title",
        "domain",
        "page_url",
        "managed_by",
        "is_active",
        "updated_at",
    )
    search_fields = ("page_title", "page_url", "managed_by")
    list_filter = ("domain", "is_active")
    inlines = [WebFormInline]

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(WebFormManager)
class WebFormManagerAdmin(ModelAdmin):
    list_display = (
        "form_name",
        "webpage",
        "submission_receiver",
        "stores_data",
        "is_active",
    )
    search_fields = ("form_name", "form_purpose", "submission_receiver")
    list_filter = ("is_active", "stores_data", "webpage")

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(DNSZone)
class DNSZoneAdmin(ModelAdmin):
    form = DNSZoneAdminForm

    list_display = (
        "domain",
        "updated_at",
    )

    search_fields = (
        "domain",
        "dns_records",
    )

    class Media:
        js = ("js/admin_row_click.js",)
