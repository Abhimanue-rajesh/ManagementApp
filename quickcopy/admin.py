from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from quickcopy.models import QuickCopy


@admin.register(QuickCopy)
class QuickCopyAdmin(ModelAdmin):
    list_display = (
        "title",
        "content",
        "updated_at",
        "copy_content",
    )

    list_display_links = ("title",)

    search_fields = (
        "title",
        "content",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Quick Copy Details",
            {
                "fields": (
                    "title",
                    "content",
                    "related_to_tickets",
                    "show_in_ticket_change",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Copy")
    def copy_content(self, obj):
        html = render_to_string(
            "quickcopy/copy_quick_item_button.html",
            {"copy_text": obj.content},
        )
        return mark_safe(html)

    class Media:
        js = (
            "quickcopy/js/quickcopy.js",
            "js/admin_row_click.js",
        )
