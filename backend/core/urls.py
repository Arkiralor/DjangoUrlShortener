from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('url_app.endpoints')),
    path('admin/', admin.site.urls),
    path('api/user/', include('user_app.endpoints'))
]
