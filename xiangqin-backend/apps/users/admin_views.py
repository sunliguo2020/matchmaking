# -*- coding: utf-8 -*-
"""
Django Admin 自定义视图 - 一键采集管理
"""
import json
import os
import datetime
import time
import threading

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from crawl_data.getUsers import getUsersByPage, getUserOrderByNew
from crawl_data.getObjectProfile import getObjectProfile
from crawl_data.getHeaders import getHeaders
from utils.tools import get_remote_image_content_file

from . import models


# 全局变量记录采集状态
crawl_status = {
    'running': False,
    'current_task': '',
    'progress': '',
    'stats': {},
    'log': []
}


def add_log(msg):
    """添加日志"""
    crawl_status['log'].append(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {msg}')
    if len(crawl_status['log']) > 200:
        crawl_status['log'] = crawl_status['log'][-200:]


@staff_member_required
def crawl_dashboard(request):
    """采集管理仪表盘"""
    from apps.tuodan.models import XingFuAnLi, Activity
    
    context = {
        'stats': {
            'users_total': models.Users.objects.count(),
            'users_with_profile': models.UsersProfile.objects.count(),
            'users_photos': models.UserProfilePhoto.objects.count(),
            'users_no_profile': models.Users.objects.filter(usersprofile__isnull=True).count(),
            'anli_total': XingFuAnLi.objects.count(),
            'activity_total': Activity.objects.count(),
        },
        'crawl_status': crawl_status,
    }
    return render(request, 'admin/crawl_dashboard.html', context)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def crawl_start(request):
    """启动采集任务"""
    if crawl_status['running']:
        return JsonResponse({'code': 400, 'msg': '已有采集任务正在运行'})
    
    task_type = request.POST.get('task_type', '')
    if not task_type:
        return JsonResponse({'code': 400, 'msg': '请指定采集任务类型'})
    
    # 重置状态
    crawl_status['running'] = True
    crawl_status['current_task'] = task_type
    crawl_status['progress'] = '准备中...'
    crawl_status['stats'] = {}
    crawl_status['log'] = []
    
    # 启动后台线程执行采集
    thread = threading.Thread(target=run_crawl_task, args=(task_type,))
    thread.daemon = True
    thread.start()
    
    return JsonResponse({'code': 200, 'msg': '采集任务已启动'})


@staff_member_required
def crawl_status_view(request):
    """获取采集状态"""
    return JsonResponse({
        'code': 200,
        'data': crawl_status
    })


def run_crawl_task(task_type):
    """执行采集任务"""
    try:
        if task_type == 'users_menutype2':
            crawl_users_menutype2()
        elif task_type == 'users_menutype3':
            crawl_users_menutype3()
        elif task_type == 'users_maylove':
            crawl_users_maylove()
        elif task_type == 'users_profiles':
            crawl_users_profiles()
        elif task_type == 'anli':
            crawl_anli()
        elif task_type == 'activity':
            crawl_activity()
        elif task_type == 'all':
            crawl_all()
        else:
            add_log(f'未知任务类型: {task_type}')
    except Exception as e:
        add_log(f'采集任务异常: {e}')
    finally:
        crawl_status['running'] = False
        crawl_status['progress'] = '已完成'
        add_log('采集任务结束')


def crawl_users_menutype2():
    """采集推荐会员(menutype=2)"""
    crawl_status['current_task'] = '推荐会员(menutype=2)'
    add_log('开始采集推荐会员(menutype=2)...')
    
    stats = {'total': 0, 'created': 0, 'updated': 0, 'skipped': 0}
    page = 1
    max_pages = 10  # 限制页数避免耗时过长
    
    while page <= max_pages:
        crawl_status['progress'] = f'正在采集第 {page} 页...'
        try:
            result = getUsersByPage(page, menutype=2)
            if result.get('code') != 200:
                add_log(f'第{page}页采集失败: {result.get("msg")}')
                break
            
            data = result.get('data', {}).get('list', [])
            if not data:
                add_log(f'第{page}页无数据，采集完成')
                break
            
            page_stats = save_users_batch(data, update=False)
            for k, v in page_stats.items():
                stats[k] += v
            stats['total'] += len(data)
            
            add_log(f'第{page}页: {len(data)}条, 新增{page_stats["created"]}, 跳过{page_stats["skipped"]}')
            page += 1
        except Exception as e:
            add_log(f'第{page}页请求失败: {e}')
            break
    
    crawl_status['stats'] = stats
    add_log(f'推荐会员(menutype=2)采集完成: 共{stats["total"]}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')


def crawl_users_menutype3():
    """采集推荐会员(menutype=3)"""
    crawl_status['current_task'] = '推荐会员(menutype=3)'
    add_log('开始采集推荐会员(menutype=3)...')
    
    stats = {'total': 0, 'created': 0, 'updated': 0, 'skipped': 0}
    page = 1
    max_pages = 10
    
    while page <= max_pages:
        crawl_status['progress'] = f'正在采集第 {page} 页...'
        try:
            result = getUsersByPage(page, menutype=3)
            if result.get('code') != 200:
                add_log(f'第{page}页采集失败: {result.get("msg")}')
                break
            
            data = result.get('data', {}).get('list', [])
            if not data:
                add_log(f'第{page}页无数据，采集完成')
                break
            
            page_stats = save_users_batch(data, update=False)
            for k, v in page_stats.items():
                stats[k] += v
            stats['total'] += len(data)
            
            add_log(f'第{page}页: {len(data)}条, 新增{page_stats["created"]}, 跳过{page_stats["skipped"]}')
            page += 1
        except Exception as e:
            add_log(f'第{page}页请求失败: {e}')
            break
    
    crawl_status['stats'] = stats
    add_log(f'推荐会员(menutype=3)采集完成: 共{stats["total"]}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')


def crawl_users_maylove():
    """采集可能喜欢的人"""
    crawl_status['current_task'] = '可能喜欢的人'
    add_log('开始采集"可能喜欢的人"...')
    
    import requests as req
    
    stats = {'total': 0, 'created': 0, 'skipped': 0}
    
    try:
        crawl_status['progress'] = '正在请求接口...'
        headers = getHeaders()
        resp = req.get(
            'https://www.sgjhw.com/pc/love/may_love',
            params={'actiontype': 'mayLove', 'pagenum': 20},
            headers=headers
        )
        result = resp.json()
        
        if result.get('code') != 200:
            add_log(f'请求失败: {result}')
            crawl_status['stats'] = stats
            return
        
        data = result.get('data', [])
        if not data:
            add_log('没有数据')
            crawl_status['stats'] = stats
            return
        
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
                    height='', weight='', city='', education='', marriage='',
                    objectID=user_id, online=0, hometown_name='',
                    flagList='[]', isvip=0, iscard=0, f_text='',
                    updatetime=timezone.now(), infoStatus='',
                    placedtop=0, revenue='', ismeet=0,
                )
                avatar_url = item.get('avatar', '')
                if avatar_url:
                    avatar_new_url = avatar_url.split('?')[0]
                    try:
                        avatar_file = get_remote_image_content_file(avatar_new_url)
                        if avatar_file:
                            user_obj.avatarURL = avatar_file
                            user_obj.avatarURL.name = os.path.basename(avatar_new_url)
                    except Exception as e:
                        add_log(f'下载头像失败: {e}')
                user_obj.save()
                stats['created'] += 1
            except Exception as e:
                add_log(f'创建用户失败 [user_id={user_id}]: {e}')
                stats['skipped'] += 1
        
        stats['total'] = len(data)
        crawl_status['stats'] = stats
        add_log(f'采集完成: 共{stats["total"]}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')
    except Exception as e:
        add_log(f'请求失败: {e}')
        crawl_status['stats'] = stats


def crawl_users_profiles():
    """批量采集用户详情和相册"""
    crawl_status['current_task'] = '用户详情和相册'
    add_log('开始批量采集用户详情和相册...')
    
    users_no_profile = models.Users.objects.filter(
        usersprofile__isnull=True
    ).values_list('user_id', flat=True)
    
    total = len(users_no_profile)
    if total == 0:
        add_log('所有会员已有详细资料，无需采集')
        crawl_status['stats'] = {'total': 0, 'success': 0, 'failed': 0}
        return
    
    add_log(f'共有 {total} 个会员没有详细资料')
    success = 0
    failed = 0
    
    for i, user_id in enumerate(users_no_profile):
        crawl_status['progress'] = f'正在采集 {i+1}/{total}: user_id={user_id}'
        
        try:
            profile = getObjectProfile(user_id)
            if profile.get('code') != 200:
                failed += 1
                add_log(f'[{i+1}/{total}] 采集失败: user_id={user_id}')
                continue
            
            _data = profile.get('data', {})
            if not _data:
                failed += 1
                continue
            
            try:
                user_obj = models.Users.objects.get(user_id=user_id)
            except models.Users.DoesNotExist:
                failed += 1
                continue
            
            if models.UsersProfile.objects.filter(memberID=user_obj).exists():
                add_log(f'[{i+1}/{total}] 已存在: user_id={user_id}')
                continue
            
            try:
                data = dict(_data)
                data['memberID'] = user_obj
                
                json_fields = ['BasicInfo', 'DetailInfo', 'ObjectInfo', 'f_text',
                              'basic', 'tag_true', 'gift']
                for field in json_fields:
                    val = _data.get(field)
                    if val is not None and not isinstance(val, str):
                        data[field] = json.dumps(val, ensure_ascii=False)
                
                basic_info = _data.get('basicInfo')
                if basic_info is not None:
                    data['basicInfo2'] = json.dumps(basic_info, ensure_ascii=False) if not isinstance(basic_info, str) else basic_info
                data.pop('basicInfo', None)
                
                new_obj = models.UsersProfile.objects.create(**data)
                
                # 处理照片
                thumb_data = _data.get('thumb')
                if thumb_data:
                    thumb_urls = []
                    if isinstance(thumb_data, str):
                        try:
                            thumb_data = json.loads(thumb_data)
                        except:
                            thumb_data = []
                    if isinstance(thumb_data, list):
                        for img in thumb_data:
                            if isinstance(img, dict):
                                url = img.get('b') or img.get('m') or img.get('s')
                                if url:
                                    thumb_urls.append(url)
                            elif isinstance(img, str):
                                thumb_urls.append(img)
                    
                    for img_url in thumb_urls:
                        try:
                            img_file = get_remote_image_content_file(img_url)
                            if img_file:
                                photo_obj = models.UserProfilePhoto(userprofile=new_obj)
                                photo_obj.image = img_file
                                photo_obj.image.name = os.path.basename(img_url)
                                photo_obj.save()
                        except Exception as e:
                            add_log(f'下载照片失败: {e}')
                
                success += 1
                if success % 10 == 0:
                    add_log(f'[{i+1}/{total}] 已成功采集 {success} 条')
            except Exception as e:
                failed += 1
                add_log(f'[{i+1}/{total}] 保存失败: user_id={user_id}, error={e}')
        except Exception as e:
            failed += 1
            add_log(f'[{i+1}/{total}] 请求失败: user_id={user_id}, error={e}')
        
        # 每10条休息一下
        if (i + 1) % 10 == 0:
            time.sleep(0.5)
    
    crawl_status['stats'] = {'total': total, 'success': success, 'failed': failed}
    add_log(f'采集完成: 成功={success}, 失败={failed}')


def crawl_anli():
    """采集幸福案例"""
    crawl_status['current_task'] = '幸福案例'
    add_log('开始采集幸福案例...')
    
    import requests as req
    from apps.tuodan.models import XingFuAnLi, Images
    
    stats = {'total': 0, 'created': 0, 'skipped': 0}
    page = 1
    max_pages = 20
    
    while page <= max_pages:
        crawl_status['progress'] = f'正在采集第 {page} 页...'
        try:
            headers = getHeaders()
            resp = req.get(
                'https://www.sgjhw.com/pc/love/anli',
                params={'page': page, 'actiontype': 'anli'},
                headers=headers
            )
            result = resp.json()
            
            if result.get('code') != 200:
                add_log(f'第{page}页采集失败')
                break
            
            data = result.get('data', [])
            if not data:
                add_log(f'第{page}页无数据')
                break
            
            for item in data:
                _id = item.get('_id')
                if not _id:
                    continue
                
                if XingFuAnLi.objects.filter(_id=_id).exists():
                    stats['skipped'] += 1
                    continue
                
                try:
                    anli_obj = XingFuAnLi(
                        _id=_id,
                        title=item.get('title', ''),
                        content=item.get('content', ''),
                        addtime=item.get('addtime', ''),
                    )
                    avatar_url = item.get('avatar', '')
                    if avatar_url:
                        try:
                            avatar_file = get_remote_image_content_file(avatar_url)
                            if avatar_file:
                                anli_obj.avatar = avatar_file
                                anli_obj.avatar.name = os.path.basename(avatar_url)
                        except Exception as e:
                            add_log(f'下载案例头像失败: {e}')
                    anli_obj.save()
                    
                    # 保存图片
                    img_list = item.get('imglist', [])
                    for img_url in img_list:
                        if img_url:
                            try:
                                img_file = get_remote_image_content_file(img_url)
                                if img_file:
                                    img_obj = Images(anliInfo=anli_obj)
                                    img_obj.image = img_file
                                    img_obj.image.name = os.path.basename(img_url)
                                    img_obj.save()
                            except Exception as e:
                                add_log(f'下载案例图片失败: {e}')
                    
                    stats['created'] += 1
                except Exception as e:
                    add_log(f'保存案例失败: {e}')
                    stats['skipped'] += 1
            
            stats['total'] += len(data)
            add_log(f'第{page}页: {len(data)}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')
            page += 1
        except Exception as e:
            add_log(f'第{page}页请求失败: {e}')
            break
    
    crawl_status['stats'] = stats
    add_log(f'幸福案例采集完成: 共{stats["total"]}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')


def crawl_activity():
    """采集相亲活动"""
    crawl_status['current_task'] = '相亲活动'
    add_log('开始采集相亲活动...')
    
    import requests as req
    from apps.tuodan.models import Activity
    
    stats = {'total': 0, 'created': 0, 'skipped': 0}
    page = 1
    max_pages = 10
    
    while page <= max_pages:
        crawl_status['progress'] = f'正在采集第 {page} 页...'
        try:
            headers = getHeaders()
            resp = req.get(
                'https://www.sgjhw.com/pc/love/activity',
                params={'page': page, 'pagenum': 10},
                headers=headers
            )
            result = resp.json()
            
            if result.get('code') != 200:
                add_log(f'第{page}页采集失败')
                break
            
            data = result.get('data', [])
            if not data:
                add_log(f'第{page}页无数据')
                break
            
            for item in data:
                aid = item.get('aid')
                if not aid:
                    continue
                
                if Activity.objects.filter(aid=aid).exists():
                    stats['skipped'] += 1
                    continue
                
                try:
                    Activity.objects.create(
                        aid=aid,
                        title=item.get('title', ''),
                        address=item.get('address', ''),
                        date_desc=item.get('date_desc', ''),
                        price=item.get('price', '0'),
                        cover_img=item.get('cover_img', ''),
                        content=item.get('content', ''),
                    )
                    stats['created'] += 1
                except Exception as e:
                    add_log(f'保存活动失败: {e}')
                    stats['skipped'] += 1
            
            stats['total'] += len(data)
            add_log(f'第{page}页: {len(data)}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')
            page += 1
        except Exception as e:
            add_log(f'第{page}页请求失败: {e}')
            break
    
    crawl_status['stats'] = stats
    add_log(f'相亲活动采集完成: 共{stats["total"]}条, 新增{stats["created"]}, 跳过{stats["skipped"]}')


def crawl_all():
    """一键采集所有数据"""
    crawl_status['current_task'] = '一键采集全部'
    add_log('=' * 40)
    add_log('开始一键采集所有数据...')
    add_log('=' * 40)
    
    crawl_users_menutype2()
    crawl_users_menutype3()
    crawl_users_maylove()
    crawl_anli()
    crawl_activity()
    crawl_users_profiles()
    
    add_log('=' * 40)
    add_log('一键采集全部完成!')


def save_users_batch(data, update=False):
    """批量保存用户数据"""
    stats = {'created': 0, 'updated': 0, 'skipped': 0}
    
    for _item in data:
        item = dict(_item)
        
        # 处理时间戳
        try:
            aware_datetime = timezone.make_aware(
                datetime.datetime.fromtimestamp(item.get('updatetime')),
                timezone.get_default_timezone()
            )
            item['updatetime'] = aware_datetime
        except (ValueError, TypeError, OSError):
            item['updatetime'] = timezone.now()
        
        # 序列化JSON字段
        for json_field in ['flagList', 'f_text', 'infoStatus']:
            val = item.get(json_field)
            if val is not None and not isinstance(val, str):
                item[json_field] = json.dumps(val, ensure_ascii=False)
        
        item['user_id'] = item.pop('id')
        item.pop('avatarURL', None)
        
        extra_fields = ['list_tip_text', 'not_login_avatar_vague', 'sex', 'house', 'house_title',
                       'revenue_title', 'jobs_id', 'jobs', 'photolist', 'is_show_meet']
        for field in extra_fields:
            item.pop(field, None)
        
        user_id = item.get('user_id')
        if not user_id:
            continue
        
        if not models.Users.objects.filter(user_id=user_id).exists():
            try:
                obj = models.Users.objects.create(**item)
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
                        add_log(f'下载头像失败: {e}')
                stats['created'] += 1
            except Exception as e:
                add_log(f'创建用户失败 [user_id={user_id}]: {e}')
                stats['skipped'] += 1
        else:
            if update:
                try:
                    models.Users.objects.filter(user_id=user_id).update(**item)
                    stats['updated'] += 1
                except Exception as e:
                    add_log(f'更新用户失败 [user_id={user_id}]: {e}')
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1
    
    return stats
