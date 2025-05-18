from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('site-admin/', admin.site.urls),
    path('short/', include('url_app.endpoints')),
    path('api/user/', include('user_app.endpoints'))
]
