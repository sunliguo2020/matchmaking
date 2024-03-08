# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/7 21:47
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        fields = '__all__'
