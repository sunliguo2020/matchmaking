from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.quickstart.serializers import GroupSerializer, UserSerializer


class UserAPIView(APIView):
    def get(self, request):
        # 从模型类中获取数据
        queryset = User.objects.all()
        # 构建序列化对象
        serializer = UserSerializer(queryset, many=True)
        # 返回结果
        return Response(serializer.data)

    def post(self, request):
        """
         处理POST请求，并返回响应。
         """
        # 从请求中获取数据，并转换为序列化器验证所需的格式
        data = request.data

        # 初始化序列化器
        serializer = UserSerializer(data=data)

        # 验证数据
        if serializer.is_valid():
            # 如果数据验证通过，保存实例
            serializer.save()
            # 返回成功响应
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 如果数据验证失败，返回错误响应
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

