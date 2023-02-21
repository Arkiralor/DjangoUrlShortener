from django.shortcuts import redirect

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from core.boilerplate.template_responses import Resp
from url_app.utils import ShortenedURLUtils

from url_app import logger


class GetAllURLsAPI(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request: Request, *args, **kwargs):
        resp = Resp()

        try:
            page = int(request.query_params.get("page", 1))
        except Exception as ex:
            resp.error = "Invalid Data."
            resp.message = f"{ex}"
            resp.status_code = 400

            logger.warn(resp.message)
            return resp.to_response()

        resp = ShortenedURLUtils.get_all_urls(page=page, user=request.user)

        return resp.to_response()


class CreateShortUrlAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, *args, **kwargs):
        user = request.user
        data = request.data
        long_url = data.get("long_url", "")

        resp = ShortenedURLUtils.create_short_url(
            user=user, long_url=long_url)

        return resp.to_response()


class GetShortUrlAPI(APIView):
    permission_classes = (AllowAny,)
    secure_http: str = "https://"

    def get(self, request: Request, slug: str = None, *args, **kwargs):

        resp = ShortenedURLUtils.get_long_url(short_url=slug)

        if resp.error:
            return resp.to_response()

        long_url = str(resp.data.get("long_url"))
        long_url = f"{self.secure_http}{long_url}" if not long_url.startswith(
            self.secure_http) else long_url

        return redirect(to=long_url, permanent=True)
