import datetime
import json
import os

from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.tools import get_remote_image_content_file
from . import models
from .serializers import UserSerializer

from crawl_data.getUsers import getUsersByPage


# Create your views here.

class UsersListCreateAPIView(ListCreateAPIView):
    queryset = models.Users
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
        for item in data:
            print(str(item).encode('utf-8'))
            # 检查id是否已存在
            if not models.Users.objects.filter(_id=item.get('id')).exists():

                print(datetime.datetime.fromtimestamp(item.get('updatetime')))

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
                    flagList=json.dumps(item.get('flagList')),
                    isvip=item.get('isvip'),
                    iscard=item.get('iscard'),
                    f_text=json.dumps(item.get('f_text')),
                    updatetime=datetime.datetime.fromtimestamp(item.get('updatetime')),
                    infoStatus=json.dumps(item.get('infoStatus')),
                    placedtop=item.get('placedtop'),
                    revenue=item.get('revenue'),
                    ismeet=item.get('ismeet'),
                )
                # 保存头像
                # 下载大图
                avatar_new_url = item.get('avatarURL').split('?')[0]
                obj.avatarURL = get_remote_image_content_file(avatar_new_url)
                # 头像名
                obj.avatarURL.name = os.path.basename(avatar_new_url)

                obj.save()

            else:
                print(f'已经存在')
        return Response({'data': result})
