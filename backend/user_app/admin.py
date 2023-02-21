from django.contrib import admin
from user_app.models import User, UserOTP, UserEmailEditToken, UserPasswordResetToken, UserPhoneEditToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "date_joined")
