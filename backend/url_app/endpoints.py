from django.urls import path, include

from url_app.apis import GetShortUrlAPI, CreateShortUrlAPI, GetAllURLsAPI

URL_PREFIX = '/'

urlpatterns = [
    path('create/', CreateShortUrlAPI.as_view(), name='create-short'),
    path('all/', GetAllURLsAPI.as_view(), name='get-all-urls'),
    path('<str:slug>/', GetShortUrlAPI.as_view(), name='redirect-long'),
]