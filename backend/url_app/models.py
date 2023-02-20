from django.db import models
from django.utils import timezone

from core.boilerplate.template_models import TemplateModel
from user_app.models import User

class ShortenedURL(TemplateModel):
    long_url = models.TextField()
    assigned_users = models.ManyToManyField(User, symmetrical=True)
    expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if not self.expiry:
            self.expiry = timezone.now() + timezone.timedelta(minutes=360)

    class Meta:
        verbose_name = "Shortened URL"
        verbose_name_plural = "Shortened URLs"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('assigned_users',))
        )

