import datetime
import json
import os

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from crawl_data.getObjectProfile import getObjectProfile
from crawl_data.getUsers import getUserOrderByNew, getUsersByPage
from utils.tools import get_remote_image_content_file
from . import models
from .filters import UserFilter
from .serializers import UserSerializer, UserProfilePhotoSerializer


# Create your views here.

class UsersListAPIView(ListAPIView):
    queryset = models.Users.objects.all()
    serializer_class = UserSerializer

    # 过滤
    filterset_fields = ('id', 'user_id', 'nickname', 'city')

    # 方式二：指定过滤类
    filterset_class = UserFilter

    # 搜索
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # search_fields = ('nickname', 'city')

    # 排序
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('id', 'nickname')


class UserPhotosAPIView(APIView):
    """
    获取会员相册照片
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        photos = []
        if user_id:
            try:
                user = models.Users.objects.get(user_id=user_id)
                profile = models.UsersProfile.objects.filter(memberID=user).first()
                if profile:
                    photo_objs = models.UserProfilePhoto.objects.filter(userprofile=profile)
                    for p in photo_objs:
                        photos.append({
                            'id': p.id,
                            'image': request.build_absolute_uri(p.image.url) if p.image else None
                        })
            except models.Users.DoesNotExist:
                pass
        return Response({'code': 200, 'data': photos, 'msg': 'success'})


class UsersCrawl(APIView):
    def get(self, request):
        """
        抓取某页的用户信息
        """
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

        # 判断查询方式: orderby=new 按最新排序, 其他或不传按默认排序
        orderby = request.query_params.get('orderby', 'default')
        try:
            if orderby == 'new':
                result = getUserOrderByNew(page)
            else:
                result = getUsersByPage(page)
        except Exception as e:
            return Response({'code': 500, "msg": f'请求采集接口失败: {e}', "data": None})

        if result.get('code') != 200:
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        data = result.get('data', {}).get('list', [])
        if not data:
            return Response({'code': 200, "msg": '该页没有数据', "data": result})

        stats = {'total': len(data), 'created': 0, 'updated': 0, 'skipped': 0}

        # 开始存入数据库中
        for _item in data:
            item = {}
            item.update(_item)

            # 处理时间戳
            try:
                aware_datetime = timezone.make_aware(
                    datetime.datetime.fromtimestamp(item.get('updatetime')),
                    timezone.get_default_timezone()
                )
                item['updatetime'] = aware_datetime
            except (ValueError, TypeError, OSError) as e:
                item['updatetime'] = timezone.now()

            # 序列化JSON字段
            for json_field in ['flagList', 'f_text', 'infoStatus']:
                val = item.get(json_field)
                if val is not None and not isinstance(val, str):
                    item[json_field] = json.dumps(val, ensure_ascii=False)

            # id修改为user_id
            item['user_id'] = item.pop('id')
            # 删除avatarURL（单独处理）
            item.pop('avatarURL', None)

            user_id = item.get('user_id')
            if not user_id:
                continue

            # 检查id是否已存在
            if not models.Users.objects.filter(user_id=user_id).exists():
                try:
                    obj = models.Users.objects.create(**item)
                    # 保存头像 下载大图
                    avatar_url = _item.get('avatarURL', '')
                    if avatar_url:
                        avatar_new_url = avatar_url.split('?')[0]
                        try:
                            avatar_file = get_remote_image_content_file(avatar_new_url)
                            if avatar_file:
                                obj.avatarURL = avatar_file
                                obj.avatarURL.name = os.path.basename(avatar_new_url)
                                obj.save()
                        except Exception as e:
                            print(f'下载头像失败 [{avatar_new_url}]: {e}')
                    stats['created'] += 1
                except Exception as e:
                    print(f'创建用户失败 [user_id={user_id}]: {e}')
                    stats['skipped'] += 1
            else:
                update_param = request.GET.get('update', 'false')
                should_update = update_param.lower() == 'true'
                if should_update:
                    try:
                        update_count = models.Users.objects.filter(user_id=user_id).update(**item)
                        if update_count > 0:
                            stats['updated'] += 1
                    except Exception as e:
                        print(f'更新用户失败 [user_id={user_id}]: {e}')
                        stats['skipped'] += 1
                else:
                    stats['skipped'] += 1

        return Response({
            'code': 200,
            'msg': f'采集完成: 新增 {stats["created"]} 条, 更新 {stats["updated"]} 条, 跳过 {stats["skipped"]} 条',
            'data': stats
        })


class UserProfileCrawl(APIView):
    """
    采集用户详情
    """

    def _parse_thumb_images(self, thumb_data):
        """解析thumb字段中的图片URL列表"""
        if not thumb_data:
            return []
        if isinstance(thumb_data, str):
            try:
                thumb_data = json.loads(thumb_data)
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(thumb_data, list):
            urls = []
            for img in thumb_data:
                if isinstance(img, dict):
                    url = img.get('b') or img.get('m') or img.get('s')
                    if url:
                        urls.append(url)
                elif isinstance(img, str):
                    urls.append(img)
            return urls
        return []

    def _save_photos(self, userprofile_obj, thumb_urls):
        """保存用户相册照片"""
        saved_count = 0
        for img_url in thumb_urls:
            try:
                img_content_file = get_remote_image_content_file(img_url)
                if img_content_file:
                    image_obj = models.UserProfilePhoto(
                        userprofile=userprofile_obj
                    )
                    image_obj.image = img_content_file
                    image_obj.image.name = os.path.basename(img_url)
                    image_obj.save()
                    saved_count += 1
            except Exception as e:
                print(f'下载用户照片失败 [{img_url}]: {e}')
        return saved_count

    def get(self, request, id, *args, **kwargs):
        if not id:
            return Response({'code': 400, 'msg': '没有传入有效的id'})

        try:
            user_obj = models.Users.objects.get(user_id=id)
        except models.Users.DoesNotExist:
            return Response({'code': 500, 'msg': f'没有查询到{id}用户'})

        # 获取详情
        try:
            profile = getObjectProfile(id)
        except Exception as e:
            return Response({'code': 500, 'msg': f'请求详情接口失败: {e}'})

        if profile.get('code') != 200:
            return Response({
                'code': profile.get('code', 500),
                'msg': '采集发生错误',
                'data': profile
            })

        _data = profile.get('data', {})
        if not _data:
            return Response({'code': 500, 'msg': '采集数据为空'})

        # 检查是否已存在
        if models.UsersProfile.objects.filter(memberID=user_obj).exists():
            return Response({'code': 201, 'msg': '用户详情已经存在'})

        try:
            # 整理数据
            data = dict(_data)
            data['memberID'] = user_obj

            # JSON字段序列化
            json_fields = ['BasicInfo', 'DetailInfo', 'ObjectInfo', 'f_text',
                          'basic', 'tag_true', 'gift']
            for field in json_fields:
                val = _data.get(field)
                if val is not None and not isinstance(val, str):
                    data[field] = json.dumps(val, ensure_ascii=False)

            # basicInfo -> basicInfo2
            basic_info = _data.get('basicInfo')
            if basic_info is not None:
                data['basicInfo2'] = json.dumps(basic_info, ensure_ascii=False) if not isinstance(basic_info, str) else basic_info
            data.pop('basicInfo', None)

            # 创建用户详情
            new_obj = models.UsersProfile.objects.create(**data)

            # 处理照片
            thumb_urls = self._parse_thumb_images(_data.get('thumb'))
            if thumb_urls:
                saved = self._save_photos(new_obj, thumb_urls)
                print(f'保存了 {saved} 张照片')

            return Response({'code': 200, 'data': profile, 'msg': '成功保存数据'})

        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'保存用户详情失败: {e}',
                'data': str(e)
            })
