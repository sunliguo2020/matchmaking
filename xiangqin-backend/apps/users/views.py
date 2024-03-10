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
        """
        抓取某页的用户信息
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)

        result = getUsersByPage(page)

        if result.get('code') == 200:
            data = result.get('data').get('list')
        else:
            print(f'抓取失败:{result}')
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        # 开始存入数据库中
        for _item in data:
            item = {}
            item.update(_item)
            print(str(item).encode('utf-8'))
            # 先处理该对象的格式：
            print(f'开始处理update属性值:{item.get("updatetime")}')

            print('先处理成日期格式', datetime.datetime.fromtimestamp(item.get('updatetime')))
            aware_datetime = timezone.make_aware(datetime.datetime.fromtimestamp(item.get('updatetime')),
                                                 timezone.get_default_timezone())
            print(f'带时区:{aware_datetime}')
            item['updatetime'] = aware_datetime

            # 再更新几个特殊的字段
            item['flagList'] = json.dumps(item.get('flagList'), ensure_ascii=False)
            item['f_text'] = json.dumps(item.get('f_text'), ensure_ascii=False)
            item['infoStatus'] = json.dumps(item.get('infoStatus'), ensure_ascii=False)

            # id修改为_id
            item['_id'] = item.pop('id')
            # 删除avatarURL
            item.pop('avatarURL')
            print(f'最后item的值:{str(item).encode("utf-8")}')

            # 检查id是否已存在
            if not models.Users.objects.filter(_id=item.get('_id')).exists():

                obj = models.Users.objects.create(**item)
                # 保存头像 下载大图
                avatar_new_url = _item.get('avatarURL').split('?')[0]
                obj.avatarURL = get_remote_image_content_file(avatar_new_url)
                # 头像的文件名
                obj.avatarURL.name = os.path.basename(avatar_new_url)

                obj.save()

            else:
                print(f'已经存在,需要更新吗?')
                update_param = request.GET.get('update', 'false')  # 默认值为'false'

                # 将字符串转换为布尔值
                should_update = update_param.lower() == 'true'
                if should_update:
                    print('开始更新对象')
                    # 先找到该对象
                    old_obj = models.Users.objects.filter(_id=item.get('_id'))
                    #
                    # # 更新该对象
                    update_count = old_obj.update(**item)
                    print(f'更新条数{update_count}')
                    # # 保存
                    # old_obj.save()

        return Response({'data': result})
