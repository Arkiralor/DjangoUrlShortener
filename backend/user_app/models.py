from django.db import models
from datetime import datetime, timedelta
import uuid

from django.core.validators import EmailValidator, RegexValidator
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from core.boilerplate.template_models import TemplateModel
from user_app.model_choices import UserChoice
from user_app.constants import UserRegex

from user_app import logger


class User(AbstractUser):
    """
    Model to store site-user information.
    """
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    first_name = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )
    middle_name = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )
    email = models.EmailField(
        validators=[
            EmailValidator(
                message="Please enter a valid email address.",
                code="invalid_email"
            )
        ],
        unique=True
    )
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=UserRegex.PHONE_REGEX_IN,
                message="Please enter a valid phone number.",
                code="invalid_phone"
            )
        ],
        unique=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(
        max_length=32, choices=UserChoice.GENDER_CHOICES, blank=True, null=True)

    user_slug = models.SlugField(max_length=250, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    unsuccessful_login_attempts = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        help_text="Number of unsuccessful login attempts"
    )
    blocked_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Blocked until"
    )

    def save(self, *args, **kwargs):
        '''
        Extended save() method to create a slug for the user.
        '''
        if not self.username:
            self.username = self.phone
        self.username = self.username.lower()

        if not self.email:
            self.email = f"{self.phone}@gmail.com"
        self.email = self.email.lower()

        if self.date_of_birth:
            res = (timezone.now().date() - self.date_of_birth)
            self.age = res.days//365.25

        self.user_slug = slugify(f"{self.username}")
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """
        Simple property tag to consolidate user's human name.
        """
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"

        else:
            return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('-date_joined', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('username',)),
            models.Index(fields=('email',)),
            models.Index(fields=('phone',)),
            models.Index(fields=('user_slug',)),
            models.Index(fields=('first_name', 'last_name')),
        )


class UserOTP(TemplateModel):
    """
    Model to hold one-time-passwords generated for users to login with.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_user'
    )
    otp = models.CharField(max_length=256)
    expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        Extended save() method to auto-generate an exipration for the OTP.
        """
        self.expiry = timezone.now() + timedelta(minutes=15)
        super(UserOTP, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User OTP'
        verbose_name_plural = 'User OTPs'
        ordering = ('-created', 'id')

        indexes = (
            models.Index(fields=('id',)),
        )


class UserPasswordResetToken(TemplateModel):
    """
    Token to be generated for users to change certain critical values
    such as:
        - Password
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)

    def __str__(self):
        return f"Reset token for {self.user.email}."

    class Meta:
        verbose_name = "User Password Reset Token"
        verbose_name_plural = "User Password Reset Tokens"
        ordering = ("user", "-created")
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',))
        )


class UserEmailEditToken(TemplateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)
    new_email = models.EmailField(
        validators=[
            EmailValidator(
                message="Please enter a valid email address.",
                code="invalid_email"
            )
        ],
        unique=False
    )
    valid_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Email edit token for {self.user.email}."

    def save(self, *args, **kwargs):
        """
        Extended save() method to auto-generate an exipration for the OTP.
        """
        self.valid_until = timezone.now() + timedelta(days=3)
        super(UserEmailEditToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "User Email Edit Token"
        verbose_name_plural = "User Email Edit Tokens"
        ordering = ("user", "-created")
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',))
        )


class UserPhoneEditToken(TemplateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)
    new_phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=UserRegex.PHONE_REGEX_IN,
                message="Please enter a valid phone number.",
                code="invalid_phone"
            )
        ],
        unique=False
    )
    valid_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Phone edit token for {self.user.email}."

    def save(self, *args, **kwargs):
        """
        Extended save() method to auto-generate an exipration for the OTP.
        """
        self.valid_until = timezone.now() + timedelta(days=3)
        super(UserPhoneEditToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "User Phone Edit Token"
        verbose_name_plural = "User Phone Edit Tokens"
        ordering = ("user", "-created")
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',))
        )
