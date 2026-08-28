from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from quickcopy.models import QuickCopy


@admin.register(QuickCopy)
class QuickCopyAdmin(ModelAdmin):
    change_list_template = "admin/quickcopy/quickcopy/change_list.html"
    list_display = (
        "title",
        "content",
        "updated_at",
        "copy_content",
        "drawer_action",
    )

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
                )
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

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<path:object_id>/drawer/",
                self.admin_site.admin_view(self.quickcopy_drawer),
                name="quickcopy_quickcopy_drawer",
            ),
        ]

        return custom_urls + urls

    def quickcopy_drawer(self, request, object_id):
        obj = self.get_object(request, object_id)

        if obj is None:
            raise Http404("Quick Copy item not found.")

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        FormClass = self.get_form(
            request,
            obj,
            change=True,
        )

        form = FormClass(
            request.POST or None,
            request.FILES or None,
            instance=obj,
        )

        if request.method == "POST" and form.is_valid():
            obj = form.save()

            self.log_change(
                request,
                obj,
                "Changed Quick Copy item from drawer.",
            )

            return JsonResponse(
                {
                    "success": True,
                    "id": obj.pk,
                    "title": obj.title,
                    "content": obj.content,
                    "updated_at": obj.updated_at.strftime("%b. %d, %Y, %I:%M %p"),
                }
            )

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "original": obj,
            "form": form,
            "object": obj,
            "model_admin": self,
        }

        return TemplateResponse(
            request,
            "quickcopy/quickcopy_drawer_form.html",
            context,
        )

    @admin.display(description="Copy")
    def copy_content(self, obj):
        html = render_to_string(
            "quickcopy/copy_quick_item_button.html",
            {
                "copy_text": obj.content,
            },
        )
        return mark_safe(html)

    @admin.display(description="")
    def drawer_action(self, obj):
        url = reverse(
            "admin:quickcopy_quickcopy_drawer",
            args=[obj.pk],
        )

        return mark_safe(f"""
            <button
                type="button"
                class="quickcopy-edit-btn"
                data-drawer-url="{url}"
                title="Edit Quick Copy"
                style="
                    border:0;
                    background:transparent;
                    cursor:pointer;
                    padding:6px;
                "
            >
                <span class="material-symbols-outlined">
                    edit
                </span>
            </button>
            """)

    class Media:

        js = (
            "quickcopy/js/quickcopy.js",
            "quickcopy/js/quickcopy_row_click.js",
            "quickcopy/js/quickcopy_drawer.js",
        )
