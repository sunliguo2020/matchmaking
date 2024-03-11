# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/7 22:42
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from . import views

urlpatterns = [
    path('list/', views.UsersListCreateAPIView.as_view(), name='users_list'),
    path('crawl/', views.UsersCrawl.as_view(), name='users_crawl'),
    path('getprofile/<int:id>/', views.UserProfileCrawl.as_view(), name='get_user_profile')
]
