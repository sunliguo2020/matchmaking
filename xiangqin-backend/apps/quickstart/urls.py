# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/6 21:44
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from apps.quickstart import views

urlpatterns = [
    path('userapiview/', views.UserAPIView.as_view(),name='userapiview'),

]