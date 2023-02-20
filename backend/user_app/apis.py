from django.shortcuts import redirect

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from user_app.utils import UserModelUtils

class UserRegisterView(APIView):

    def post(self, request:Request, *args, **kwargs):
        user, resp = UserModelUtils.register_new_user(data=request.data)

        return Response(
            {
                "error": resp.error,
                "message": resp.message,
                "data": resp.data
            },
            status=resp.status_code
        )