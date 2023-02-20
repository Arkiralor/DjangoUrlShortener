from typing import List

from rest_framework import status

from core.boilerplate.template_responses import Resp
from user_app.models import User
from url_app.models import ShortenedURL
from url_app.serializers import ShortenedUrlSerializer

from url_app import logger


class ShortenedURLUtils:

    @classmethod
    def create_short_url(cls, users: List[User] = [], long_url: str = None):
        resp = Resp()

        if len(users) == 0 or not long_url:
            resp.error = "Invalid Parameters"
            resp.message = "Both UserList and LongUrl are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(f"{resp.message}")
            return resp

        for item in users:
            item = item.id

        data = {
            "long_url": long_url,
            "assigned_user": users
        }

        deserialized = ShortenedUrlSerializer(data=data)
        if not deserialized.is_valid():
            resp.error = "Model Data Error"
            resp.message = f'{deserialized.errors}'
            resp.data = data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)

            return resp

        deserialized.save()
        resp.data = deserialized.data
        resp.status_code = status.HTTP_201_CREATED

        return resp

    @classmethod
    def get_long_url(cls, short_url: str = None):
        resp = Resp()
        if not short_url:
            resp.error = "Invalid Parameter"
            resp.message = "Short URL is required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)
            return resp

        url_obj = ShortenedURL.objects.filter(pk=short_url).first()
        if not url_obj:
            resp.error = "Not Found"
            resp.message = "Invalid short url."
            resp.data = {
                "shortUrl": short_url
            }
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp

        serialized = ShortenedUrlSerializer(url_obj).data

        resp.message = "Url retrieved successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        return resp
