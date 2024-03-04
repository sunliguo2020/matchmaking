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
            "commentstatus",
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
        print(f'validated_data:{validated_data}')

        # validated_data 现在包含 imgurl 字段，它是一个 InMemoryUploadedFile 对象
        image_data = validated_data.pop('imgurl', [])
        # 保存除imgulr之外的数据
        s_obj = models.XingFuAnLi.objects.create(**validated_data)

        print(f'self.context:{self._context}')
        image_data = self._context.get('request').FILES
        # 上传的所有图片信息
        print(f"imgrul 最新值：{image_data}")
        print(f"imgrul 所有的值：{image_data.getlist('imgurl')}")
        for ele in image_data.getlist('imgurl'):
            models.Images.objects.create(anliInfo=s_obj, image=ele)
        return s_obj
