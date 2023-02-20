from django.urls import path, include

from user_app.apis import UserRegisterView, UserPasswordLoginAPI

URL_PREFIX = 'api/user/'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register-new-user'),
    path('login/v1/', UserPasswordLoginAPI.as_view(), name='user-password-login')
]