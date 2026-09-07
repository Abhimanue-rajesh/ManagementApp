from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import (
    Currency,
    PaymentCard,
    PaymentTiming,
    SubscriptionTracker,
)


@admin.register(PaymentCard)
class PaymentCardAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(PaymentTiming)
class PaymentTimingAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SubscriptionTracker)
class SubscriptionTrackerAdmin(ModelAdmin):
    list_display = (
        "platform",
        "status_badge",
        "email_used",
        "card_used",
        "currency",
        "pricing",
        "payment_timing",
        "debit_date",
        "days_until_debit",
    )

    list_filter = (
        "status",
        "currency",
        "payment_timing",
        "card_used",
        "debit_date",
        "platform",
    )

    search_fields = (
        "platform",
        "email_used",
        "card_used__name",
        "currency__code",
        "payment_timing__name",
        "used_for",
        "notes",
    )

    autocomplete_fields = (
        "card_used",
        "currency",
        "payment_timing",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "days_until_debit",
        "is_due_soon",
        "is_overdue",
    )

    ordering = ("status", "debit_date")

    fieldsets = (
        (
            "Subscription Details",
            {
                "fields": (
                    "platform",
                    "status",
                    "email_used",
                    "card_used",
                    "used_for",
                )
            },
        ),
        (
            "Payment Details",
            {
                "fields": (
                    "currency",
                    "pricing",
                    "payment_timing",
                    "debit_date",
                )
            },
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
        (
            "System Info",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "days_until_debit",
                    "is_due_soon",
                    "is_overdue",
                )
            },
        ),
    )

    @display(
        description="Status",
        label={
            "active": "success",
            "inactive": "danger",
            "on_hold": "warning",
            "cancelled": "danger",
        },
    )
    def status_badge(self, obj):
        return obj.status

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

    class Media:
        js = ("js/admin_row_click.js",)
