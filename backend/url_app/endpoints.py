from django.urls import path, include

from url_app.apis import GetShortUrlAPI, CreateShortUrlAPI

URL_PREFIX = '/'

urlpatterns = [
    path('<str:slug>/', GetShortUrlAPI.as_view(), name='redirect-long'),
    path('create/', CreateShortUrlAPI.as_view(), name='create-short')
]