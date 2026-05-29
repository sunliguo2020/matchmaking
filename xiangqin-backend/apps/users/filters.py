# -*- coding: utf-8 -*-
"""
@author: sunliguo
@contact: QQ376440229
@Created on: 2024-03-30 18:17
"""
from django_filters import rest_framework as filters

from apps.users import models


class UserFilter(filters.FilterSet):
    # 模糊匹配
    nickname = filters.CharFilter(field_name='nickname', lookup_expr='icontains', label='昵称模糊查询')
    min_age = filters.NumberFilter(field_name='age', lookup_expr='gte')
    max_age = filters.NumberFilter(field_name='age', lookup_expr='lte')
    user_id = filters.NumberFilter(field_name='user_id', lookup_expr='exact', label='用户ID精确查询')
    gender = filters.NumberFilter(field_name='gender', lookup_expr='exact', label='性别(1=男,2=女)')
    city = filters.CharFilter(field_name='city_name', lookup_expr='icontains', label='城市模糊查询')

    class Meta:
        model = models.Users
        fields = ['nickname', 'id', 'user_id', 'age', 'min_age', 'max_age', 'gender', 'city']
