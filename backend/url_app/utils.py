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

    DEFAULT_EXPIRY: int = 360
    BLANK: str = ""

    @classmethod
    def get_expiry(cls, expiry_mins:int=0) -> str:
        # if expiry_mins <= 0 or expiry_mins > 1440:
        #     expiry_mins = cls.DEFAULT_EXPIRY

        if not expiry_mins in range(0, 1441):
            expiry_mins = cls.DEFAULT_EXPIRY

        expiry = timezone.localtime(timezone.now()) + timezone.timedelta(minutes=expiry_mins)
        expiry = expiry.strftime("%Y-%m-%d %H:%M:%S")

        return expiry

    @classmethod
    def create_short_url(cls, user: User = None, long_url: str = None, expiry_mins:int=0)->Resp:
        resp = Resp()

        if not user or not long_url or long_url == cls.BLANK:
            resp.error = "Invalid Parameters"
            resp.message = "Both UserList and LongUrl are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp
        
        expiry = cls.get_expiry(expiry_mins=expiry_mins)

        data = {
            "long_url": long_url,
            "assigned_user": user.id,
            "expiry": expiry
        }

        deserialized = ShortenedUrlSerializer(data=data)
        if not deserialized.is_valid():
            resp.error = "Model Data Error"
            resp.message = f'{deserialized.errors}'
            resp.data = data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())

            return resp

        deserialized.save()
        resp.message = "URL shortened successfully."
        resp.data = deserialized.data
        resp.status_code = status.HTTP_201_CREATED

        logger.info(resp.to_text())

        return resp

    @classmethod
    def get_long_url(cls, short_url: str = None):
        resp = Resp()
        if not short_url:
            resp.error = "Invalid Parameter"
            resp.message = "Short URL is required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        url_obj = ShortenedURL.objects.filter(pk=short_url).first()
        if not url_obj:
            resp.error = "Not Found"
            resp.message = "Invalid short url."
            resp.data = {
                "shortUrl": short_url
            }
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp
        
        if not url_obj.is_active:
            resp.error = "Link Inactive"
            resp.message = f"The shortlink: {url_obj.short_url} is inactive."
            resp.data = {
                "shortUrl": short_url
            }
            resp.status_code = status.HTTP_401_UNAUTHORIZED

            logger.warning(resp.to_text())
            return resp

        if url_obj.expiry <= timezone.localtime(timezone.now()):
            resp.error = "Link Expired"
            resp.message = f"The shortlink: {url_obj.short_url} expired at {url_obj.expiry.strftime('%Y-%m-%d %H:%M:%S')}."
            resp.data = {
                "shortUrl": short_url
            }
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warning(resp.to_text())
            url_obj.inactivate()
            return resp

        serialized = ShortenedUrlSerializer(url_obj).data

        resp.message = f"URL \'{url_obj.long_url}\' retrieved successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def get_all_urls(cls, page:int=1, user:User=None):
        resp = Resp()
        
        if not user or not (user.is_superuser or user.is_staff):
            resp.error = "Permission Denied"
            resp.message = "Only admins are allowed to access this data."
            resp.status_code = status.HTTP_401_UNAUTHORIZED

            logger.warning(resp.to_text())
            return resp

        objs = ShortenedURL.objects.all()

        ## Of course we paginate this, I have no intention to blow up the instance with a virtual torrent of data.
        paginator = Paginator(objs, per_page=settings.ITEMS_PER_PAGE)
        objs = paginator.get_page(page)

        serialized = ShortenedUrlSerializer(objs, many=True).data

        data = {
            "hits": len(serialized),
            "results": serialized,
            "page": page
        }

        resp.data = data
        resp.message = f"Items in page #{page} retrieved successfully."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())

        return resp
        
