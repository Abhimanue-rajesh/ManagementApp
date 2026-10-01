from django.conf import settings
from django.db import models


class Tutorial(models.Model):
    title = models.CharField(max_length=200)

    content = models.TextField(
        blank=True,
        help_text="Paste the complete tutorial in Markdown format.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tutorials",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title
