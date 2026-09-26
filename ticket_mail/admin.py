import re

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import escape, format_html
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from .models import (
    AllowedEmailDomain,
    SupportTicket,
    TicketAttachment,
    TicketEmailMessage,
)

INLINE_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


class TicketEmailMessageInline(StackedInline):
    model = TicketEmailMessage
    extra = 0
    can_delete = False
    collapsible = True

    fields = (
        "received_at",
        "sender_email",
        "subject",
        "preview_link",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Original email")
    def preview_link(self, obj):
        if not obj.pk:
            return "—"

        url = reverse(
            "admin:ticket_mail_supportticket_email_preview",
            args=[obj.pk],
        )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">' "Open email preview</a>",
            url,
        )


class TicketAttachmentInline(TabularInline):
    model = TicketAttachment
    extra = 0
    can_delete = False

    fields = (
        "original_name",
        "size",
        "image_preview",
        "download_link",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Image")
    def image_preview(self, obj):
        if not obj.pk or obj.content_type.lower() not in INLINE_IMAGE_TYPES:
            return "—"

        url = reverse(
            "admin:ticket_mail_supportticket_attachment",
            args=[obj.pk],
        )
        return format_html(
            '<img src="{}?inline=1" alt="{}" loading="lazy" '
            'style="max-width:160px;max-height:110px;'
            'object-fit:contain;border-radius:8px;" />',
            url,
            obj.original_name,
        )

    @admin.display(description="File")
    def download_link(self, obj):
        if not obj.pk:
            return "—"

        url = reverse(
            "admin:ticket_mail_supportticket_attachment",
            args=[obj.pk],
        )
        return format_html('<a href="{}">Download</a>', url)


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
    search_fields = (
        "subject",
        "requester_name",
        "requester_email",
        "description",
    )
    ordering = ("-created_at",)
    list_select_related = ("assigned_to",)

    inlines = (
        TicketEmailMessageInline,
        TicketAttachmentInline,
    )

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
            "Original email",
            {"fields": ("original_email_preview",)},
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
        readonly = (
            "ticket_number",
            "original_email_preview",
            "confirmation_sent_at",
            "created_at",
            "updated_at",
        )

        if obj is None:
            return readonly

        return readonly + (
            "subject",
            "requester_name",
            "requester_email",
            "description",
            "received_at",
        )

    @admin.display(description="Ticket #", ordering="id")
    def ticket_number_display(self, obj):
        return obj.ticket_number

    @admin.display(description="Email as received")
    def original_email_preview(self, obj):
        if not obj or not obj.pk:
            return "The email preview appears after the ticket is created."

        first_message = obj.email_messages.order_by("received_at").first()
        if not first_message:
            return "No imported email is linked to this ticket."

        url = reverse(
            "admin:ticket_mail_supportticket_email_preview",
            args=[first_message.pk],
        )
        return format_html(
            '<iframe src="{}" title="Original ticket email" '
            'sandbox="allow-same-origin" '
            'style="width:100%;height:520px;'
            "border:1px solid #d1d5db;border-radius:10px;"
            'background:white;"></iframe>',
            url,
        )

    def get_urls(self):
        custom_urls = [
            path(
                "email/<int:message_id>/preview/",
                self.admin_site.admin_view(self.email_preview_view),
                name="ticket_mail_supportticket_email_preview",
            ),
            path(
                "attachment/<int:attachment_id>/",
                self.admin_site.admin_view(self.attachment_view),
                name="ticket_mail_supportticket_attachment",
            ),
        ]
        return custom_urls + super().get_urls()

    def email_preview_view(self, request, message_id):
        ticket_message = get_object_or_404(
            TicketEmailMessage.objects.select_related("ticket"),
            pk=message_id,
        )

        if not self.has_view_permission(
            request,
            obj=ticket_message.ticket,
        ):
            raise PermissionDenied

        if ticket_message.html_body:
            html = ticket_message.html_body

            # Replace cid: image references with protected admin URLs.
            for attachment in ticket_message.attachments.exclude(content_id=""):
                if attachment.content_type.lower() not in INLINE_IMAGE_TYPES:
                    continue

                image_url = (
                    reverse(
                        "admin:ticket_mail_supportticket_attachment",
                        args=[attachment.pk],
                    )
                    + "?inline=1"
                )

                html = re.sub(
                    re.escape(f"cid:{attachment.content_id}"),
                    lambda match: image_url,
                    html,
                    flags=re.IGNORECASE,
                )
        else:
            # Older imported messages may have no stored HTML.
            html = (
                '<pre style="white-space:pre-wrap;'
                'font:14px/1.5 sans-serif;">'
                f"{escape(ticket_message.body)}"
                "</pre>"
            )

        response = HttpResponse(html, content_type="text/html; charset=utf-8")
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        response["Content-Security-Policy"] = (
            "sandbox allow-same-origin; "
            "default-src 'none'; "
            "script-src 'none'; "
            "img-src 'self' data:; "
            "style-src 'unsafe-inline'; "
            "font-src 'self'; "
            "form-action 'none'; "
            "base-uri 'none'; "
            "frame-ancestors 'self'"
        )
        return response

    def attachment_view(self, request, attachment_id):
        attachment = get_object_or_404(
            TicketAttachment.objects.select_related("ticket"),
            pk=attachment_id,
        )

        if not self.has_view_permission(request, obj=attachment.ticket):
            raise PermissionDenied

        inline = (
            request.GET.get("inline") == "1"
            and attachment.content_type.lower() in INLINE_IMAGE_TYPES
        )

        response = FileResponse(
            attachment.file.open("rb"),
            as_attachment=not inline,
            filename=attachment.original_name,
        )
        response["Content-Type"] = (
            attachment.content_type.lower() if inline else "application/octet-stream"
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response


@admin.register(AllowedEmailDomain)
class AllowedEmailDomainAdmin(ModelAdmin):
    list_display = ("domain", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("domain",)
    ordering = ("domain",)
    readonly_fields = ("created_at",)
