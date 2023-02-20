from django.shortcuts import redirect

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from url_app.utils import ShortenedURLUtils
from user_app.utils import UserModelUtils

class CreateShortUrlAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request:Request, *args, **kwargs):
        users = [request.user]
        data = request.data
        long_url = data.get("long_url", "")

        resp = ShortenedURLUtils.create_short_url(users=users, long_url=long_url)

        return Response(
            {
                "error": resp.error,
                "message": resp.message,
                "data": resp.data
            },
            status=resp.status_code
        )

class GetShortUrlAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request:Request, slug:str=None, *args, **kwargs):

        resp = ShortenedURLUtils.get_long_url(short_url=slug)

        if resp.error:
            return Response(
                {
                    "error": resp.error,
                    "message": resp.message,
                    "data": resp.data
                },
                status=resp.status_code
            )

        return redirect(to=resp.data.get('long_url'), permanent=True)

