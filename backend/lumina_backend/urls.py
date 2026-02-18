"""
URL configuration for lumina_backend project.
"""
from django.contrib import admin
from django.urls import path, include

from api.views import root_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', root_view, name='root'),
]
