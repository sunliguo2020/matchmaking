# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/3 15:48
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from rest_framework import serializers
from . import models


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Images
        fields = '__all__'


class AnLiSerializer(serializers.ModelSerializer):
    imgurl = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='images-detail'
    )

    class Meta:
        model = models.XingFuAnLi
        fields = [
            "_id",
            "comment_num",
            "zan_status",
            "commentStatus",
            "avatar",
            "title",
            "content",
            "hits",
            "commentlist",
            "addtime",
            "nickname",
            'imgurl'
        ]

    def create(self, validated_data):
        """
        自定义新增模型类实例的方法
        """
        # 从 validated_data 中移除 imgurl（它是只读的 HyperlinkedRelatedField）
        validated_data.pop('imgurl', None)

        # 保存案例主对象
        s_obj = models.XingFuAnLi.objects.create(**validated_data)

        # 从请求中获取上传的图片文件
        request = self.context.get('request')
        if request and request.FILES:
            image_data = request.FILES
            for ele in image_data.getlist('imgurl'):
                models.Images.objects.create(anliInfo=s_obj, image=ele)

        return s_obj

    def update(self, instance, validated_data):
        pass


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = '__all__'
