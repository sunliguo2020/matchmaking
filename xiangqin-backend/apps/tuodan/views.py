import json
import os.path
from datetime import datetime

from django.http import Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from crawl_data.getAnli import getAnliByPage
from utils.CustomPagination import CustomPagination
from utils.tools import get_remote_image_content_file
from . import models
from .serializers import ActivitySerializer, AnLiSerializer


# Create your views here.


class AnLi(ListCreateAPIView):
    serializer_class = AnLiSerializer
    queryset = models.XingFuAnLi.objects.all()
    pagination_class = CustomPagination

    def post(self, request):
        """
        重写post方法，返回自定义Response
        :param request:
        :return:
        """
        print(f"request.FILES:{request.FILES}")
        # request.FILES:<MultiValueDict: {
        # 'avatar':[<InMemoryUploadedFile: 2024-01-28_181414.png (image/png)>],
        # 'imgurl': [<InMemoryUploadedFile: accessKeyCode.jpg (image/jpeg)>,
        # <InMemoryUploadedFile: 10964343-efdfe0e040e3526f.webp (image/webp)>]}>
        print(f"request.data:{request.data}")
        # request.data:<QueryDict: {
        # '_id': ['500'],
        # 'comment_num': ['121'],
        # 'title': ['sdf'],
        # 'content': ['2232'],
        # 'hits': ['22'],
        # 'commentlist': ['2'],
        # 'nickname': ['红娘'],
        # 'avatar': [<InMemoryUploadedFile: 2024-01-28_181414.png (image/png)>],
        # 'imgurl': [<InMemoryUploadedFile: accessKeyCode.jpg (image/jpeg)>,
        # <InMemoryUploadedFile: 10964343-efdfe0e040e3526f.webp (image/webp)>]}>

        # HyperlinkedRelatedField 需要 context
        serializer = AnLiSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            print(f"serializer.validated_data:{serializer.validated_data}")
            serializer.save()
            return Response({"code": 200, "data": serializer.data, "msg": "新增数据成功!"})
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
    """
    采集幸福案例
    
    从相亲网站采集幸福案例数据并存入本地数据库。
    
    ### 请求参数:
    - **page** (int, 可选): 页码，默认1
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "msg": "采集完成: 成功 X 条, 跳过 X 条, 失败 X 条",
      "data": {"total": 10, "success": 5, "skipped": 5, "failed": 0}
    }
    ```
    """

    def _parse_date(self, date_string):
        """安全解析日期字符串"""
        if not date_string:
            return datetime.now().date()
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").date()
            except (ValueError, TypeError):
                return datetime.now().date()

    def _download_image(self, url):
        """下载远程图片，失败时返回 None"""
        if not url:
            return None
        try:
            content_file = get_remote_image_content_file(url)
            if content_file:
                content_file.name = os.path.basename(url)
            return content_file
        except Exception as e:
            print(f"下载图片失败 [{url}]: {e}")
            return None

    def _save_single_case(self, item):
        """保存单个幸福案例，返回保存结果"""
        case_id = item.get('id')
        if not case_id:
            return {'status': 'skipped', 'reason': '缺少 id 字段'}

        # 检查是否已存在
        if models.XingFuAnLi.objects.filter(_id=case_id).exists():
            return {'status': 'skipped', 'reason': '已存在'}

        try:
            # 创建案例对象
            obj = models.XingFuAnLi(
                _id=case_id,
                comment_num=item.get('comment_num', ''),
                zan_status=bool(item.get('zan_status', False)),
                commentStatus=bool(item.get('commentStatus', False)),
                title=item.get('title', ''),
                content=item.get('content', ''),
                hits=item.get('hits', ''),
                commentlist=json.dumps(item.get('commentlist', []), ensure_ascii=False),
                addtime=self._parse_date(item.get('addtime')),
                nickname=item.get('nickname', ''),
            )

            # 下载并保存头像
            avatar_file = self._download_image(item.get('avatar'))
            if avatar_file:
                obj.avatar = avatar_file

            # 先保存主对象，获取 id
            obj.save()

            # 下载并保存案例图片
            img_urls = item.get('imgurl', [])
            if img_urls:
                for img_url in img_urls:
                    img_content_file = self._download_image(img_url)
                    if img_content_file:
                        try:
                            image_obj = models.Images(anliInfo=obj)
                            image_obj.image = img_content_file
                            image_obj.save()
                        except Exception as e:
                            print(f"保存图片记录失败 [{img_url}]: {e}")

            return {'status': 'success', 'case_id': case_id}

        except Exception as e:
            print(f"保存案例失败 [id={case_id}]: {e}")
            return {'status': 'failed', 'case_id': case_id, 'error': str(e)}

    def get(self, request):
        """
        根据 page 采集幸福案例
        """
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

        # 采集数据
        try:
            result = getAnliByPage(page)
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'请求采集接口失败: {e}',
                'data': None
            })

        if result.get('code') != 200:
            return Response({
                'code': 400,
                'msg': '抓取幸福案例失败',
                'data': result
            })

        data = result.get('data', {}).get('list', [])
        if not data:
            return Response({
                'code': 200,
                'msg': '该页没有数据',
                'data': {'total': 0, 'success': 0, 'skipped': 0, 'failed': 0}
            })

        # 统计信息
        stats = {'total': len(data), 'success': 0, 'skipped': 0, 'failed': 0, 'details': []}

        # 逐条保存案例
        for item in data:
            save_result = self._save_single_case(item)
            stats['details'].append(save_result)
            status_key = save_result.get('status')
            if status_key in stats:
                stats[status_key] += 1

        return Response({
            'code': 200,
            'msg': f'采集完成: 成功 {stats["success"]} 条, 跳过 {stats["skipped"]} 条, 失败 {stats["failed"]} 条',
            'data': stats
        })


class ActivityList(ListAPIView):
    """
    获取活动列表
    """
    serializer_class = ActivitySerializer
    queryset = models.Activity.objects.all()
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class ActivityCrawl(APIView):
    """
    采集相亲活动
    
    从相亲网站采集相亲活动数据并存入本地数据库。
    
    ### 请求参数:
    - **page** (int, 可选): 页码，默认1
    - **pagenum** (int, 可选): 每页数量，默认5
    
    ### 返回数据:
    ```json
    {
      "code": 200,
      "msg": "采集完成: 新增 X 条, 跳过 X 条",
      "data": {"total": 5, "created": 3, "skipped": 2}
    }
    ```
    """
    def get(self, request):
        import requests as req
        from crawl_data.getHeaders import getHeaders

        page = request.query_params.get('page', 1)
        pagenum = request.query_params.get('pagenum', 5)
        try:
            page = int(page)
            pagenum = int(pagenum)
        except (ValueError, TypeError):
            page = 1
            pagenum = 5

        try:
            headers = getHeaders()
            resp = req.get(
                'https://www.sgjhw.com/pc/love/act_list_903',
                params={'actiontype': 'act_list_903', 'page': page, 'pagenum': pagenum},
                headers=headers
            )
            result = resp.json()
        except Exception as e:
            return Response({'code': 500, "msg": f'请求活动列表接口失败: {e}', "data": None})

        if result.get('code') != 200:
            return Response({'code': 400, "msg": '抓取失败', "data": result})

        data = result.get('data', {}).get('list', [])
        if not data:
            return Response({'code': 200, "msg": '该页没有数据', "data": result})

        stats = {'total': len(data), 'created': 0, 'skipped': 0}

        for item in data:
            aid = item.get('aid')
            if not aid:
                continue

            if models.Activity.objects.filter(aid=aid).exists():
                stats['skipped'] += 1
                continue

            try:
                models.Activity.objects.create(
                    aid=aid,
                    title=item.get('title', ''),
                    address=item.get('address', ''),
                    cover_img=item.get('cover_img', ''),
                    big_img=item.get('big_img', ''),
                    date_desc=item.get('date_desc', ''),
                    date_act=item.get('date_act', ''),
                    price=item.get('price', ''),
                    vip_price=item.get('vip_price', ''),
                    money_sex1=item.get('money_sex1', ''),
                    money_sex2=item.get('money_sex2', ''),
                    location=item.get('location', ''),
                    is_over=bool(item.get('is_over', False)),
                    over_content=item.get('over_content', ''),
                )
                stats['created'] += 1
            except Exception as e:
                print(f'创建活动失败 [aid={aid}]: {e}')
                stats['skipped'] += 1

        return Response({
            'code': 200,
            'msg': f'采集完成: 新增 {stats["created"]} 条, 跳过 {stats["skipped"]} 条',
            'data': stats
        })
