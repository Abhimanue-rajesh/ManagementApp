from django.conf import settings
from django.db import models
from django.utils import timezone


class PaymentCard(models.Model):
    name = models.CharField(max_length=150, unique=True)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Payment Card"
        verbose_name_plural = "Payment Cards"

    def __str__(self):
        return self.name


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.code


class PaymentTiming(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Payment Timing"
        verbose_name_plural = "Payment Timings"

    def __str__(self):
        return self.name


class SubscriptionTracker(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]

    platform = models.CharField(
        max_length=150,
        default="No Platform",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    email_used = models.EmailField(blank=True, null=True)

    card_used = models.ForeignKey(
        PaymentCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )

    used_for = models.TextField(blank=True)

    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )

    pricing = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    payment_timing = models.ForeignKey(
        PaymentTiming,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )

    debit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    last_debit_processed_date = models.DateField(
        null=True,
        blank=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["debit_date", "platform"]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return str(self.platform)

    def days_until_debit(self):
        if not self.debit_date:
            return None
        return (self.debit_date - timezone.localdate()).days

    def is_due_soon(self):
        days = self.days_until_debit()
        return days is not None and 0 <= days <= 7

    def is_overdue(self):
        days = self.days_until_debit()
        return days is not None and days < 0


class CardTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    card = models.ForeignKey(
        PaymentCard,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default="debit",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subscription = models.ForeignKey(
        SubscriptionTracker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="card_transactions",
    )

    transaction_date = models.DateField(
        default=timezone.localdate,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        verbose_name = "Card Transaction"
        verbose_name_plural = "Card Transactions"

    def __str__(self):
        return f"{self.card} - {self.transaction_type} - {self.amount}"
