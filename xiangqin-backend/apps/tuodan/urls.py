# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/3 15:56
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from django.urls import path

from . import views

urlpatterns = [
    path('anli/', views.AnLi.as_view(), name='anli_list'),
    path('images/<pk>/', views.ImagesDetailView.as_view(), name='images-detail'),
    path('crawl/', views.AnLiCrawl.as_view())
]
