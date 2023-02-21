from django.shortcuts import redirect

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from user_app.utils import UserModelUtils

class UserRegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request:Request, *args, **kwargs):
        user, resp = UserModelUtils.register_new_user(data=request.data)

        return resp.to_response()

class UserPasswordLoginAPI(APIView):

    permission_classes = (AllowAny,)

    def post(self, request:Request, *args, **kwargs):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        resp = UserModelUtils.login_via_password(username=username, email=email, password=password)

        return resp.to_response()