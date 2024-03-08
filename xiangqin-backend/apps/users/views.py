import datetime
import json
import os

from django.shortcuts import render
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.tools import get_remote_image_content_file
from . import models
from .serializers import UserSerializer

from crawl_data.getUsers import getUsersByPage


# Create your views here.

class UsersListCreateAPIView(ListCreateAPIView):
    queryset = models.Users.objects.all()
    serializer_class = UserSerializer


class UsersCrawl(APIView):
    def get(self, request):
        page = request.query_params.get('page', 1)

        result = getUsersByPage(page)

        if result.get('code') == 200:
            data = result.get('data').get('list')
        else:
            print(f'抓取失败:{result}')
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        # 开始存入数据库中
        for _item in data:
            item = dict.update(_item)
            print(str(item).encode('utf-8'))
            # 先处理该对象的格式：
            print(datetime.datetime.fromtimestamp(item.get('updatetime')))
            aware_datetime = timezone.make_aware(datetime.datetime.fromtimestamp(item.get('updatetime')),
                                                 timezone.get_default_timezone())
            item['updatetime'] = aware_datetime

            # 检查id是否已存在
            if not models.Users.objects.filter(_id=item.get('id')).exists():

                obj = models.Users.objects.create(
                    _id=item.get('id'),
                    age=item.get('age'),
                    height=item.get('height'),
                    weight=item.get('weight'),
                    city=item.get('city'),
                    education=item.get('education'),
                    gender=item.get('gender'),
                    marriage=item.get('marriage'),
                    nickname=item.get('nickname'),
                    objectID=item.get('objectID'),
                    jobs_title=item.get('jobs_title'),
                    online=item.get('online'),
                    city_name=item.get('city_name'),
                    hometown_name=item.get('hometown_name'),
                    #  TODO list 的保存格式问题
                    flagList=json.dumps(item.get('flagList'), ensure_ascii=False),
                    isvip=item.get('isvip'),
                    iscard=item.get('iscard'),
                    #
                    f_text=json.dumps(item.get('f_text'), ensure_ascii=False),
                    # 时间格式问题 ，带时区
                    # 将其转换为aware datetime对象
                    updatetime=item.get('updatetime'),
                    #
                    infoStatus=json.dumps(item.get('infoStatus'), ensure_ascii=False),
                    placedtop=item.get('placedtop'),
                    revenue=item.get('revenue'),
                    ismeet=item.get('ismeet'),
                )
                # 保存头像 下载大图
                avatar_new_url = item.get('avatarURL').split('?')[0]
                obj.avatarURL = get_remote_image_content_file(avatar_new_url)
                # 头像的文件名
                obj.avatarURL.name = os.path.basename(avatar_new_url)

                obj.save()

            else:
                print(f'已经存在,需要更新吗')
                # 先找到该对象
                # 更新该对象

        return Response({'data': result})
