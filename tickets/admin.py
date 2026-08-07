from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import redirect
from django.utils import timezone
from unfold.admin import ModelAdmin

from quickcopy.models import QuickCopy
from tickets.models import (
    SupportTicket,
    SupportTicketHistory,
    TicketRouting,
    TicketStatus,
)


@admin.register(SupportTicketHistory)
class SupportTicketHistoryAdmin(ModelAdmin):
    list_display = (
        "ticket",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "changed_at",
    )
    search_fields = (
        "ticket__ticket_name",
        "ticket__ticket_number",
        "field_name",
    )
    list_filter = (
        "field_name",
        "changed_at",
    )

    readonly_fields = (
        "ticket",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "changed_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SupportTicketHistoryInline(admin.TabularInline):
    model = SupportTicketHistory
    extra = 0
    can_delete = False

    fields = (
        "changed_at",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
    )

    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    change_list_template = "tickets/change_list.html"
    list_display = (
        "ticket_number",
        "ticket_name",
        "status",
        "is_urgent",
        "updated_on",
    )
    list_filter = (
        "routing",
        "status",
        "created_at",
    )
    list_editable = ("status",)
    search_fields = (
        "ticket_number",
        "ticket_name",
        "status_note",
        "raised_by",
    )
    autocomplete_fields = (
        "routing",
        "status",
        "related_ticket",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    inlines = [
        SupportTicketHistoryInline,
    ]
    fieldsets = (
        (
            "Ticket Details",
            {
                "fields": (
                    "ticket_number",
                    "ticket_name",
                    "routing",
                    "raised_by",
                    "is_urgent",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "last_updated_date",
                    "status_note",
                    "related_ticket",
                    "created_at",
                )
            },
        ),
    )

    @admin.display(description="Updated")
    def updated_on(self, obj):
        return obj.last_updated_date

    @admin.display(description="Created")
    def created_on(self, obj):
        return obj.created_at

    class Media:
        css = {"all": ("css/ticket_admin.css",)}
        js = (
            "js/admin_row_click.js",
            "quickcopy/js/quickcopy.js",  # This is needed for the ticket related quick copy functionality
        )

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and request.POST.get("_quick_add_ticket"):
            ticket_number = request.POST.get("ticket_number")

            try:
                SupportTicket.objects.create(
                    user=request.user,
                    ticket_number=ticket_number.strip() if ticket_number else None,
                    ticket_name=request.POST.get("ticket_name"),
                    routing_id=request.POST.get("routing") or None,
                    status_id=request.POST.get("status") or None,
                    raised_by=request.POST.get("raised_by") or "Not Recorded",
                )

                messages.success(request, "Support ticket created successfully.")

            except ValidationError as error:
                if hasattr(error, "message_dict"):
                    first_error = list(error.message_dict.values())[0][0]
                else:
                    first_error = error.messages[0]

                messages.error(request, first_error)

            return redirect(request.path)
        ticket_status_counts = TicketStatus.objects.annotate(
            ticket_count=Count("tickets")
        ).order_by("name")

        extra_context = extra_context or {}
        extra_context["ticket_routings"] = TicketRouting.objects.all()
        extra_context["ticket_statuses"] = TicketStatus.objects.all()
        extra_context["ticket_status_counts"] = ticket_status_counts
        extra_context["quick_copy_items"] = QuickCopy.objects.filter(
            related_to_tickets=True
        ).order_by("title")
        extra_context["stale_tickets"] = (
            SupportTicket.objects.filter(
                last_updated_date__lt=timezone.localdate() - timezone.timedelta(days=1)
            )
            .exclude(status__name__iexact="closed")
            .select_related(
                "routing",
                "status",
            )
        )

        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.ticket_number = (
            str(obj.ticket_number).strip() if obj.ticket_number else None
        )

        if change:
            old_obj = SupportTicket.objects.get(pk=obj.pk)

            fields_to_track = [
                "ticket_name",
                "routing",
                "status",
                "status_note",
                "raised_by",
                "related_ticket",
                "is_urgent",
            ]

            for field in fields_to_track:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)

                if old_value != new_value:
                    SupportTicketHistory.objects.create(
                        ticket=obj,
                        field_name=field,
                        old_value=str(old_value) if old_value else "",
                        new_value=str(new_value) if new_value else "",
                        changed_by=request.user,
                    )

        if not obj.pk:
            obj.user = request.user

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.GET:
            return queryset

        return queryset.exclude(status__name__iexact="Closed")


@admin.register(TicketRouting)
class TicketRoutingAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)


@admin.register(TicketStatus)
class TicketStatusAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    class Media:
        js = ("js/admin_row_click.js",)
