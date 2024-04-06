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

    class Meta:
        model = models.Users
        fields = ['nickname', 'id', 'age', 'min_age', 'max_age']
