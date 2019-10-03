from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('users/', include('users.urls')),
    path('files/', include('files.urls')),
]
