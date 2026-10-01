from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Tutorial


@admin.register(Tutorial)
class TutorialAdmin(ModelAdmin):
    list_display = (
        "title",
        "created_by",
        "is_published",
        "updated_at",
    )
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "introduction")
    readonly_fields = ("created_by", "created_at", "updated_at")
    list_filter_submit = True
    list_fullwidth = True

    fieldsets = (
        (
            "Tutorial",
            {
                "fields": (
                    ("title", "is_published"),
                    "content",
                ),
            },
        ),
        (
            "Record Details",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == "content" and formfield:
            formfield.widget.attrs.update(
                {
                    "rows": 10,
                    "style": (
                        "width: 100%; max-width: none; "
                        "height: 50rem; min-height: 4.5rem; "
                        "resize: vertical;"
                    ),
                }
            )

        return formfield

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
