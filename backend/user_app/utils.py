from secrets import token_urlsafe, choice
from typing import List
from os import environ
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, QuerySet
from django.utils import timezone

from core.boilerplate.template_responses import Resp
from user_app.constants import UserRegex
from user_app.models import User
from user_app.serializers import UserOutputSerializer, UserRegisterSerializer, UserOTPSerializer, UserPasswordResetTokenSerializer

from user_app import logger


class JWTUtils:
    """
    Utilities for basic operation on JWT.
    """
    @classmethod
    def get_tokens_for_user(cls, user: User = None):
        refresh = RefreshToken.for_user(user)

        return {
            'refreshToken': str(refresh),
            'accessToken': str(refresh.access_token),
        }


class UserModelUtils:
    """
    Utilities for operations on the User model.
    """

    USER_REGEX = UserRegex
    DEFAULT_PASSWORD = settings.DEFAULT_PASSWORD
    EDITABLE_FIELDS = (
        "first_name",
        "middle_name",
        "last_name",
        "country_of_residence",
        "gender",
        "date_of_birth"
    )

    @classmethod
    def check_if_user_exists(cls, username:str=None, phone:str=None, email:str=None, *args, **kwargs)->bool:
        """
        Check if a user with the given parameters is registered in the system.
            username
            phone
            email
        """
        user_check = User.objects.filter(
            Q(username__iexact=username)
            | Q(phone__iexact=phone)
            | Q(email__iexact=email)
        ).exists()

        return user_check

    @classmethod
    def register_new_user(cls, data: dict = None, is_admin: bool = False) -> tuple[User, Resp]:
        resp = Resp()

        if not data.get("email") or data.get("email") == "":
            data["email"] = f"{data.get('phone')}@mslate.ai"
        if not data.get("password", None):
            data['password'] = environ.get("DEFAULT_PASSWORD")

        if cls.check_if_user_exists(username=data.get('username'), phone=data.get('phone'), email=data.get('email')):
            resp.error = "400: User already exists."
            resp.data = data
            resp.message = f"A user with the given credentials (username | email | phone) already exists."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return None, Resp

        
        # prithoo: We are validating the password here because we cannot do that once the password
        # has been hashed and salted.
        if not UserRegex.PASSWORD_REGEX.search(data.get('password')):
            resp.data = data
            resp.message = "Password MUST contain 1 UPPERCASE character, 1 lowercase character, 1 special character and 1 numerical character."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return None, resp
        data['password'] = make_password(data.get('password'))

        if not is_admin:
            if 'is_staff' in data.keys():
                data['is_staff'] = False
            if 'is_superuser' in data.keys():
                data['is_superuser'] = False

        data['is_active'] = False

        deserialized = UserRegisterSerializer(data=data)
        is_valid = deserialized.is_valid()

        if not is_valid:
            resp.data = deserialized.data
            resp.error = "400: Invalid Data"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)

            return None, resp

        deserialized.save()
        resp.data = deserialized.data
        resp.message = f"User {deserialized.instance.username} registered succesfully."
        resp.status_code = status.HTTP_201_CREATED

        return deserialized.instance, resp

    @classmethod
    def block_user(cls, user:User=None, blocked_until:int=settings.OTP_ATTEMPT_TIMEOUT, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user:
            logger.warn("User Instance Required.")
            resp.error = "User Instance Required."
            resp.message = f"Attempt to block user due to too many failed login attempts failed."
            return resp

        user.unsuccessful_login_attempts = 0
        user.blocked_until = timezone.now() + timezone.timedelta(minutes=blocked_until)
        user.save()

        resp.error = "User Blocked"
        resp.message = f"Too many unsuccessfull login attempts. User {user.email} is blocked for {blocked_until} minutes, until {user.blocked_until}."
        resp.data = {
            "user": user.id,
            "blockedUntil": user.blocked_until.strftime("YYYY-MM-dd HH:mm:ss")
        }
        resp.status_code = status.HTTP_401_UNAUTHORIZED
        return resp


    @classmethod
    def login_via_password(cls, username:str=None, email:str=None, password:str=None, *args, **kwargs)->Resp:
        resp = Resp()
        user:User = None

        if not username and email:
            resp.error = "Invalid Request"
            resp.message = "Either username or email are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        if username and not email:
            user = User.objects.filter(username__iexact=username, is_active=True).first()
        elif email and not username:
            user = User.objects.filter(email__iexact=email, is_active=True).first()
        else:
            resp.error = "Invalid Request"
            resp.message = "Send either the USERNAME or the EMAIL, not both."
            resp.status_code = status.HTTP_300_MULTIPLE_CHOICES
            return resp

        if not user:
            resp.error = "User not found."
            resp.message = "User not found for the given credentials, please check again."
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp

        if user.blocked_until > timezone.now():
            resp.error = "Login Blocked"
            resp.message = f"The user is blocked from logging in until {user.blocked_until}."
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

        if not check_password(password=password, encoded=user.password):
            user.unsuccessful_login_attempts += 1
            user.save()

            if user.unsuccessful_login_attempts > settings.OTP_ATTEMPT_LIMIT:
                resp = cls.block_user(user=user)
                return resp

            resp.error = "Invalid Credentials"
            resp.message = "The entered password is incorrect."
            resp.data = {
                "username": username,
                "email": email,
                "password": password,
                "attemptsLeft": settings.OTP_ATTEMPT_LIMIT - user.unsuccessful_login_attempts
            }
            resp.status_code = status.HTTP_403_FORBIDDEN
            return resp

        if user.unsuccessful_login_attempts != 0:
            user.unsuccessful_login_attempts = 0
            user.save()

        tokens = JWTUtils.get_tokens_for_user(user=user)
        resp.message = f"User {user.email} logged in successfully."
        resp.data = {
            "user": user.id,
            "tokens": tokens,
            "login": timezone.now().strftime("YYYY-MM-dd HH:mm:ss")
        }
        resp.status_code=status.HTTP_200_OK

        logger.info(f"User {user.email} logged in at {resp.data.get('login')} via password.")

        return resp
