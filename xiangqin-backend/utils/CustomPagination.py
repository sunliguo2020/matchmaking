# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/6 21:14
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    自定义分页类
    """
    page_size = 10  # 每页显示的数目
    page_query_param = 'page'  # 页码的参数名称
    page_size_query_param = 'size'  # 每页显示数量的参数名称
    max_page_size = 50  # 每页最多显示的数目

    def get_paginated_response(self, data):
        """
        自定义分页返回格式
        """
        return Response({
            'code': 200,
            'msg': 'success',
            'data': data,
            'current_page': self.page.number,
            'next_page': self.get_next_link(),
            'previous_page': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,

        }, status=status.HTTP_200_OK)
