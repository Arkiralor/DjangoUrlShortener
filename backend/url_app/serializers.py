from rest_framework.serializers import ModelSerializer
from url_app.models import ShortenedURL

class ShortenedUrlSerializer(ModelSerializer):

    class Meta:
        model = ShortenedURL
        fields = '__all__'