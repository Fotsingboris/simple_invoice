from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views

urlpatterns = [
    path('admin-tenant/', admin.site.urls),
    path('',include('download.urls')),
]
