from datetime import datetime
import json
import os.path

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from . import models
from .serializers import AnLiSerializer, ImagesSerializer

from crawl_data.getAnli import getAnliByPage
from utils.tools import get_remote_image_content_file
from utils.CustomPagination import CustomPagination


# Create your views here.


class AnLi(ListCreateAPIView):
    serializer_class = AnLiSerializer
    queryset = models.XingFuAnLi.objects.all()
    pagination_class = CustomPagination

    def post(self, request):
        print(f"request.FILES:{request.FILES}")
        print(f"request.data:{request.data}")
        serializer = AnLiSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            print(f"serializer.validated_data:{serializer.validated_data}")
            serializer.save()
            return Response({"code": 200, "data": serializer.data, "msg": "插入成功!"})
        else:
            error_data = {"code": 402, "data": "", "msg": serializer.errors}

            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class ImagesDetailView(APIView):
    def get_object(self, pk):
        try:
            return models.Images.objects.get(pk=pk)
            # return models.Images.objects.filter(anliInfo_id__exact=pk)
        except models.Images.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # context = {"request": request}
        # article = self.get_object(pk)
        # print(f"查找到所有的Image对象{article}")
        # serializer = ImagesSerializer(instance=article, context=context)
        # return Response(serializer.data)
        image_instance = self.get_object(pk)
        image_url = image_instance.image.url
        return HttpResponseRedirect(image_url)


class AnLiCrawl(APIView):
    def get(self, request):
        page = request.query_params.get('page', 1)
        result = getAnliByPage(page)

        if result.get('code') == 200:
            data = result.get('data').get('list')
        else:
            print('抓取失败')
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        # 开始存入数据库中
        for item in data:
            print(item)
            # print(item.get('id'))
            # 检查id是否已存在
            if not models.XingFuAnLi.objects.filter(_id=item.get('id')).exists():
                # 创建除 avatar和imgurl的对象
                date_string = item.get('addtime')
                date_object = datetime.strptime(date_string, "%Y-%m-%d").date()

                obj = models.XingFuAnLi.objects.create(
                    _id=item.get('id'),
                    comment_num=item.get('comment_num'),
                    zan_status=item.get('zan_status'),
                    commentStatus=item.get('commentStatus'),
                    title=item.get('title'),
                    content=item.get('content'),
                    hits=item.get('hits'),
                    commentlist=json.dumps(item.get('commentlist')),
                    addtime=date_object,
                    nickname=item.get('nickname'),
                )
                # 保存头像
                obj.avatar = get_remote_image_content_file(item.get('avatar'))
                # 头像名
                obj.avatar.name = os.path.basename(item.get('avatar'))

                # 保存图片
                if len(item.get('imgurl')) > 0:
                    for img in item.get('imgurl'):
                        print(img)
                        img_content_file = get_remote_image_content_file(img)
                        image_obj = models.Images.objects.create(anliInfo=obj)
                        image_obj.image = img_content_file
                        image_obj.image.name = os.path.basename(img)

                        image_obj.save()

                obj.save()

            else:
                print(f'已经存在')
        return Response({'data': result})
