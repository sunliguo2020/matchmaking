"""
URL configuration for xiangqin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls

from xiangqin import settings

urlpatterns = [
    re_path(r'^docs/', include_docs_urls(title='接口文档')),
    path('admin/', admin.site.urls),
    # url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api-auth/', include('rest_framework.urls')),
    path('api/tuodan/', include('apps.tuodan.urls')),
    path('api/users/', include('apps.users.urls')),
    path('quickstart/', include('apps.quickstart.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
