from secrets import token_hex, token_urlsafe, choice
from typing import List

from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, QuerySet
from django.utils import timezone

from rest_framework import status

from core.boilerplate.template_responses import Resp
from user_app.models import User, UserOTP
from user_app.serializers import UserOutputSerializer, UserRegisterSerializer, UserOTPSerializer, UserPasswordResetTokenSerializer

from user_app import logger


class OTPHelper:
    VALID_NUMBERS = (str(int(num)) for num in range(100, 999, 1))
    DEFAULT_SIZE: int = 4
    OTP_EXPIRY: int = 30

    @classmethod
    def create_otp(cls, size: int = None) -> str:
        tokens: List[str] = []
        if not size:
            size = cls.DEFAULT_SIZE

        interator: int = 0

        while interator < size:
            tokens.append(choice(cls.VALID_NUMBERS))

        otp = ''.join(tokens)
        return otp

    @classmethod
    def assign_otp_to_user(cls, otp: str = None, user: User = None, *args, **kwargs):
        if not otp or not user:
            return False

        encoded_otp = make_password(otp)
        otp_expiry = timezone.now() + timezone.timedelta(minutes=cls.OTP_EXPIRY)
        data = {
            "user": f"{user.id}",
            "otp": encoded_otp,
            "expiry": otp_expiry.strftime("YYYY-MM-dd HH:mm:ss")
        }

        serialized = UserOTPSerializer(data=data)
        if not serialized.is_valid():
            logger.warn(f"{serialized.errors}")
            return False

        serialized.save()
        return serialized.instance.id

    @classmethod
    def check_otp_for_user(cls, txn_id: str = None, otp: str = None, user: User = None, *args, **kwargs):
        resp = Resp()
        otp_obj = UserOTP.objects.filter(
            Q(pk=txn_id)
            & Q(user=user)
        ).order_by("-created").first()
        if not otp_obj:
            resp.error = "OTP Not Found"
            resp.message = "Either the user did not request an OTP or incorrect transaction ID."
            resp.data = {
                "txn_id": txn_id,
                "otp": otp,
                "user": f'{user.id}'
            }
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp

        if otp_obj.expiry < timezone.now():
            resp.error = "OTP Expired"
            resp.message = f"The OTP expired at {otp_obj.expiry}. Please request a new OTP."
            resp.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return resp

        if not check_password(otp, otp_obj.otp):
            resp.error = "Incorrect OTP"
            resp.message = "The provided OTP is incorrect."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            return resp

        resp.error = None
        resp.message = "OTP Authenticated."
        resp.data = True
        resp.status_code = status.HTTP_200_OK

        return resp
