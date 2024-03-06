# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/6 21:38
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from django.contrib.auth.models import Group, User
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    groups = serializers.CharField()

    def create(self, validated_data):
        """
        创建并返回一个新的模型实例
        :param validated_data: 
        :return: 
        """
        # 使用validated_data 来创建模型实例
        s_obj = User.objects.create(**validated_data)

        return s_obj

    def update(self, instance, validated_data):
        """
        更新一个已存在的模型实例
        :param instance:已经存在的模型实例
        :param validated_data:
        :return:
        """
        instance.field1 = validated_data.get('field1', instance.field1)

        # 保存模型实例
        instance.save()
        # 返回更新后的模型实例
        return instance


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
