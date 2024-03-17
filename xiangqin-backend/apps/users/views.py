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

from crawl_data.getUsers import getUsersByPage, getUserOrderByNew
from crawl_data.getObjectProfile import getObjectProfile


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

        # 判断查询方式 orderby  vip real new 和空
        result = getUserOrderByNew(page)

        if result.get('code') == 200:
            data = result.get('data').get('list')
        else:
            print(f'抓取失败:{result}')
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        # 开始存入数据库中
        for _item in data:
            item = {}
            item.update(_item)
            # print(str(item).encode('utf-8'))
            # 先处理该对象的格式：
            # print(f'开始处理update属性值:{item.get("updatetime")}')
            # print('先处理成日期格式', datetime.datetime.fromtimestamp(item.get('updatetime')))
            aware_datetime = timezone.make_aware(datetime.datetime.fromtimestamp(item.get('updatetime')),
                                                 timezone.get_default_timezone())
            # print(f'带时区:{aware_datetime}')
            item['updatetime'] = aware_datetime

            # 再更新几个特殊的字段
            item['flagList'] = json.dumps(item.get('flagList'), ensure_ascii=False)
            item['f_text'] = json.dumps(item.get('f_text'), ensure_ascii=False)
            item['infoStatus'] = json.dumps(item.get('infoStatus'), ensure_ascii=False)

            # id修改为user_id
            item['user_id'] = item.pop('id')
            # 删除avatarURL
            item.pop('avatarURL')
            # print(f'最后item的值:{str(item).encode("utf-8")}')

            # 检查id是否已存在
            if not models.Users.objects.filter(user_id=item.get('user_id')).exists():
                print(f'b不存在，准备插入')

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
                    old_obj = models.Users.objects.filter(user_id=item.get('user_id'))
                    #
                    # # 更新该对象
                    update_count = old_obj.update(**item)
                    print(f'更新条数{update_count}')

        return Response({'data': result})


class UserProfileCrawl(APIView):
    """
    采集用户详情
    """

    def get(self, request, id, *args, **kwargs):
        # print(id, args, kwargs)
        # id = request.query_params.get('id', '')
        profile = {}
        if not id:
            return Response({'code': 400, 'msg': '没有传入有效的id'})

        user_obj = models.Users.objects.get(user_id=id)
        if not user_obj:
            return Response({'code': 500, 'msg': f'没有查询到{id}用户'})

        # 获取详情
        profile = getObjectProfile(id)
        # 获取到有效数据
        if profile.get('code', '') == 200:
            _data = profile.get('data', '')
            print(f"获取到的原始数据：{json.dumps(_data, ensure_ascii=False)}")
            data = {}
            data.update(_data)

            # 整理数据
            data['memberID'] = user_obj
            data['BasicInfo'] = json.dumps(_data.get('BasicInfo'), ensure_ascii=False)
            data['DetailInfo'] = json.dumps(_data.get('DetailInfo'), ensure_ascii=False)
            data['ObjectInfo'] = json.dumps(_data.get('ObjectInfo'), ensure_ascii=False)
            data['f_text'] = json.dumps(_data.get('f_text'), ensure_ascii=False)
            data['basic'] = json.dumps(_data.get('basic'), ensure_ascii=False)
            data['basicInfo2'] = json.dumps(_data.get('basicInfo'), ensure_ascii=False)
            data.pop('basicInfo')
            data['tag_true'] = json.dumps(_data.get('tag_true'), ensure_ascii=False)
            data['gift'] = json.dumps(_data.get('gift'), ensure_ascii=False)

            print(f"整理好的数据:{data}")

            if not models.UsersProfile.objects.filter(memberID=user_obj).exists():
                # 创建新用户详情
                new_obj = models.UsersProfile.objects.create(**data)
                print(f"新建用户信息：{new_obj},照片信息：{new_obj.thumb}")

                # 检查是否有照片
                if new_obj.thumb and not models.UserProfilePhoto.objects.filter(user=new_obj).exists():
                    print(f'抓取到照片，但照片对象不存在')
                    for img in new_obj.thumb:
                        img = img.get('b')
                        img_content_file = get_remote_image_content_file(img)
                        image_obj = models.UserProfilePhoto.objects.create(user=new_obj)
                        image_obj.image = img_content_file
                        image_obj.image.name = os.path.basename(img)

                        image_obj.save()
                        print(f'新建对象：{image_obj}')
                else:
                    print(f"照片对象已经存在!检查照片是否已经下载")
                    exist_obj = models.UsersProfile.objects.filter(memberID=user_obj)
                    # 检查thumb是否有数据，有则检查图片是否已经下载？
            else:
                print(f'用户详情{models.UsersProfile.objects.filter(memberID=user_obj)}已经存在')
                return Response({'code': 201, 'msg': '用户详情已经存在'})

            return Response({'code': 200, 'data': '', 'msg': '成功保存数据'})

        else:
            return Response({'code': profile.get('code', '500'),
                             'msg': '采集发生错误，原始数据见data!',
                             'data': profile})
