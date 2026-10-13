from django.db import models


class QuickCopy(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    related_to_tickets = models.BooleanField(default=False)
    show_in_ticket_change = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quick Copy"
        verbose_name_plural = "Quick Copy Items"

    def __str__(self):
        return self.title
