from django.contrib import admin
from url_app.models import ShortenedURL

@admin.register(ShortenedURL)
class ShortenedUrlAdmin(admin.ModelAdmin):
    list_display = ("id", "long_url", "expiry")
