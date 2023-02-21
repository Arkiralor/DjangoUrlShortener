from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone

from rest_framework import status

from core.boilerplate.template_responses import Resp
from user_app.models import User
from url_app.models import ShortenedURL
from url_app.serializers import ShortenedUrlSerializer

from url_app import logger


class ShortenedURLUtils:

    @classmethod
    def create_short_url(cls, user: User = None, long_url: str = None):
        resp = Resp()

        if not user or not long_url:
            resp.error = "Invalid Parameters"
            resp.message = "Both UserList and LongUrl are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(f"{resp.message}")
            return resp

        data = {
            "long_url": long_url,
            "assigned_user": user.id
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
        resp.message = "URL shortened successfully."
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

        if url_obj.expiry <= timezone.now():
            resp.error = "Link Expired"
            resp.message = f"The shortlink: {url_obj.short_url} expired at {url_obj.expiry.strftime('YYYY-MM-dd HH:mm:ss')}."
            resp.data = {
                "shortUrl": short_url
            }
            resp.status_code = status.HTTP_403_FORBIDDEN
            return resp

        serialized = ShortenedUrlSerializer(url_obj).data

        resp.message = "Url retrieved successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        return resp

    @classmethod
    def get_all_urls(cls, page:int=1, user:User=None):
        resp = Resp()
        
        if not user or not (user.is_superuser or user.is_staff):
            resp.error = "Permission Denied"
            resp.message = "Only admins are allowed to access this data."
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

        objs = ShortenedURL.objects.all()

        ## Of course we paginate this, I have no intention to blow up the instance with a virtual torrent of data.
        paginator = Paginator(objs, per_page=settings.ITEMS_PER_PAGE)
        objs = paginator.get(page)

        serialized = ShortenedUrlSerializer(objs, many=True).data

        data = {
            "hits": len(serialized),
            "results": serialized,
            "page": page
        }

        resp.data = data
        resp.message = f"Items in page #{page} retrieved successfully."
        resp.status_code = status.HTTP_200_OK

        return resp
        
