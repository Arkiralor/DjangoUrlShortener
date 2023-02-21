from os import environ
from django.db import models
from django.utils import timezone

from core.boilerplate.template_models import TemplateModel
from user_app.models import User

class ShortenedURL(TemplateModel):
    long_url = models.TextField()
    short_url = models.TextField(blank=True, null=True)
    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if not self.expiry:
            self.expiry = timezone.now() + timezone.timedelta(minutes=360)
        
        self.short_url = f"{environ.get('APP_NAME')}/{self.id}"
        super(ShortenedURL, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Shortened URL"
        verbose_name_plural = "Shortened URLs"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
        )

