import json
import os.path
from datetime import datetime

from django.http import Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from crawl_data.getAnli import getAnliByPage
from utils.CustomPagination import CustomPagination
from utils.tools import get_remote_image_content_file
from . import models
from .serializers import AnLiSerializer


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
