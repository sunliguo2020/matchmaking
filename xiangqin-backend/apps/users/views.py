import datetime
import json
import os

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from crawl_data.getHeaders import getHeaders
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

    # 过滤 - 使用自定义FilterSet支持gender和city过滤
    filterset_class = UserFilter

    # 排序
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
    """
    采集推荐会员列表
    
    从相亲网站采集推荐会员数据并存入本地数据库。
    
    ### 请求参数:
    - **page** (int, 可选): 页码，默认1
    - **menutype** (int, 可选): 推荐分类，2=推荐会员, 3=推荐会员
    - **lasttime** (int, 可选): 时间戳，用于翻页采集更早的数据。
      翻页方式：用当前页中最小updatetime作为下一页的lasttime
    - **orderby** (str, 可选): 排序方式，'new'=按最新排序
    - **update** (str, 可选): 是否更新已存在的用户，'true'=更新
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "msg": "采集完成: 新增 X 条, 更新 X 条, 跳过 X 条",
      "data": {"total": 10, "created": 5, "updated": 0, "skipped": 5}
    }
    ```
    """
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
        menutype = request.query_params.get('menutype')
        lasttime = request.query_params.get('lasttime')
        print(f'[DEBUG] UsersCrawl: page={page}, menutype={menutype}, lasttime={lasttime}')
        try:
            if orderby == 'new':
                result = getUserOrderByNew(page)
            else:
                result = getUsersByPage(page, menutype=menutype, lasttime=lasttime)
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
            # 删除Users模型中不存在的字段（menutype=3接口返回的额外字段）
            extra_fields = ['list_tip_text', 'not_login_avatar_vague', 'sex', 'house', 'house_title',
                           'revenue_title', 'jobs_id', 'jobs', 'photolist', 'is_show_meet']
            for field in extra_fields:
                item.pop(field, None)

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
    
    从相亲网站采集指定用户的详细资料（包括基本资料、详细资料、择偶要求等）和相册照片。
    
    ### 请求参数:
    - **id** (int, 路径参数, 必填): 用户ID
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "data": {...},
      "msg": "成功保存数据"
    }
    ```
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
                'msg': f'采集失败: {profile.get("data", "未知错误")}',
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


class CrawlStatsAPIView(APIView):
    """
    爬取接口统计
    
    汇总所有爬取接口的统计数据，包括会员总数、幸福案例数、活动数等。
    
    ### 请求参数:
    无
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "data": {
        "users": {"total": 30, "with_profile": 5, "photos": 20, "latest_update": "..."},
        "anli": {"total": 133, "latest_update": "..."},
        "activity": {"total": 25},
        "crawl_interfaces": [...]
      },
      "msg": "success"
    }
    ```
    """
    def get(self, request):
        from apps.tuodan.models import XingFuAnLi, Activity
        
        # 用户相关统计
        total_users = models.Users.objects.count()
        users_with_profile = models.UsersProfile.objects.count()
        total_photos = models.UserProfilePhoto.objects.count()
        
        # 幸福案例统计
        total_anli = XingFuAnLi.objects.count()
        
        # 活动统计
        total_activity = Activity.objects.count()
        
        # 获取最新数据时间
        latest_user = models.Users.objects.order_by('-updatetime').first()
        latest_anli = XingFuAnLi.objects.order_by('-addtime').first()
        
        return Response({
            'code': 200,
            'data': {
                'users': {
                    'total': total_users,
                    'with_profile': users_with_profile,
                    'photos': total_photos,
                    'latest_update': latest_user.updatetime if latest_user else None,
                },
                'anli': {
                    'total': total_anli,
                    'latest_update': str(latest_anli.addtime) if latest_anli else None,
                },
                'activity': {
                    'total': total_activity,
                },
                'crawl_interfaces': [
                    {
                        'name': '推荐会员',
                        'url': '/api/users/crawl/',
                        'params': 'page, menutype(2/3), lasttime, orderby(new)',
                        'description': '采集推荐会员列表，支持menutype=2/3分类，支持lasttime翻页'
                    },
                    {
                        'name': '可能喜欢的人',
                        'url': '/api/users/maylove/',
                        'params': 'pagenum',
                        'description': '采集"可能喜欢的人"推荐会员'
                    },
                    {
                        'name': '用户详情',
                        'url': '/api/users/getprofile/<id>/',
                        'params': 'id (路径参数)',
                        'description': '采集指定用户的详细资料和相册'
                    },
                    {
                        'name': '幸福案例',
                        'url': '/api/tuodan/crawl/',
                        'params': 'page',
                        'description': '采集幸福案例列表'
                    },
                    {
                        'name': '相亲活动',
                        'url': '/api/tuodan/activity/',
                        'params': 'page, pagenum',
                        'description': '采集相亲活动列表'
                    },
                ]
            },
            'msg': 'success'
        })


class MayLoveCrawl(APIView):
    """
    采集"可能喜欢的人"推荐会员
    
    从相亲网站采集"可能喜欢的人"推荐会员数据并存入本地数据库。
    
    ### 请求参数:
    - **pagenum** (int, 可选): 采集数量，默认20
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "msg": "采集完成: 新增 X 条, 跳过 X 条",
      "data": {"total": 20, "created": 4, "skipped": 16}
    }
    ```
    """
    def get(self, request):
        import requests as req
        pagenum = request.query_params.get('pagenum', 20)
        try:
            pagenum = int(pagenum)
        except (ValueError, TypeError):
            pagenum = 20

        try:
            headers = getHeaders()
            resp = req.get(
                'https://www.sgjhw.com/pc/love/may_love',
                params={'actiontype': 'mayLove', 'pagenum': pagenum},
                headers=headers
            )
            result = resp.json()
        except Exception as e:
            return Response({'code': 500, "msg": f'请求may_love接口失败: {e}', "data": None})

        if result.get('code') != 200:
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        data = result.get('data', [])
        if not data:
            return Response({'code': 200, "msg": '没有数据', "data": result})

        stats = {'total': len(data), 'created': 0, 'skipped': 0}

        for item in data:
            user_id = item.get('id')
            if not user_id:
                continue

            if models.Users.objects.filter(user_id=user_id).exists():
                stats['skipped'] += 1
                continue

            try:
                user_obj = models.Users(
                    user_id=user_id,
                    nickname=item.get('nickname', ''),
                    gender=item.get('sex', 0),
                    jobs_title=item.get('jobs_title', ''),
                    city_name=item.get('city_name', ''),
                    age=item.get('age', ''),
                    # 以下为必填字段，提供默认值
                    height='',
                    weight='',
                    city='',
                    education='',
                    marriage='',
                    objectID=user_id,
                    online=0,
                    hometown_name='',
                    flagList='[]',
                    isvip=0,
                    iscard=0,
                    f_text='',
                    updatetime=timezone.now(),
                    infoStatus='',
                    placedtop=0,
                    revenue='',
                    ismeet=0,
                )
                # 下载头像
                avatar_url = item.get('avatar', '')
                if avatar_url:
                    avatar_new_url = avatar_url.split('?')[0]
                    try:
                        avatar_file = get_remote_image_content_file(avatar_new_url)
                        if avatar_file:
                            user_obj.avatarURL = avatar_file
                            user_obj.avatarURL.name = os.path.basename(avatar_new_url)
                    except Exception as e:
                        print(f'下载头像失败 [{avatar_new_url}]: {e}')

                user_obj.save()
                stats['created'] += 1
            except Exception as e:
                print(f'创建用户失败 [user_id={user_id}]: {e}')
                stats['skipped'] += 1

        return Response({
            'code': 200,
            'msg': f'采集完成: 新增 {stats["created"]} 条, 跳过 {stats["skipped"]} 条',
            'data': stats
        })
