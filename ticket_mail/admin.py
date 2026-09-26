from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline

from ticket_mail.models import AllowedEmailDomain, SupportTicket, TicketEmailMessage


class TicketEmailMessageInline(StackedInline):
    model = TicketEmailMessage
    extra = 0
    can_delete = False
    collapsible = True

    fields = (
        "received_at",
        "sender_email",
        "subject",
        "body",
        "gmail_message_id",
        "gmail_thread_id",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    list_display = (
        "ticket_number_display",
        "subject",
        "requester_email",
        "status",
        "assigned_to",
        "received_at",
    )
    list_display_links = ("ticket_number_display", "subject")
    list_filter = ("status", "assigned_to", "received_at")
    search_fields = ("subject", "requester_name", "requester_email", "description")
    ordering = ("-created_at",)
    list_select_related = ("assigned_to",)
    inlines = (TicketEmailMessageInline,)

    fieldsets = (
        (
            "Ticket",
            {
                "fields": (
                    "ticket_number",
                    "subject",
                    "requester_name",
                    "requester_email",
                    "description",
                    "received_at",
                )
            },
        ),
        (
            "Team workflow",
            {"fields": ("status", "assigned_to")},
        ),
        (
            "Email confirmation",
            {"fields": ("confirmation_sent_at",)},
        ),
        (
            "Record",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        system_fields = (
            "ticket_number",
            "confirmation_sent_at",
            "created_at",
            "updated_at",
        )
        if obj is None:
            return system_fields

        # Preserve the original request received by email.
        return system_fields + (
            "subject",
            "requester_name",
            "requester_email",
            "description",
            "received_at",
        )

    @admin.display(description="Ticket #", ordering="id")
    def ticket_number_display(self, obj):
        return obj.ticket_number


@admin.register(AllowedEmailDomain)
class AllowedEmailDomainAdmin(ModelAdmin):
    list_display = ("domain", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("domain",)
    ordering = ("domain",)
    readonly_fields = ("created_at",)
