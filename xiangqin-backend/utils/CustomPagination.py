# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/6 21:14
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'msg': 'success',
            'data': {
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'total_count': self.page.paginator.count,
                'result': data
            }
        })
