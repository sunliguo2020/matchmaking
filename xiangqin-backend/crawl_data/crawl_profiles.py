# -*- coding: utf-8 -*-
"""
批量采集会员详细资料和相册

采集所有没有详细资料的会员的详细资料和相册照片。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'xiangqin.settings'

import django
django.setup()

import urllib.request
import json
import time

from apps.users import models

# 获取所有没有详细资料的会员
users_without_profile = models.Users.objects.filter(
    usersprofile__isnull=True
).values_list('user_id', flat=True)

total = len(users_without_profile)
print(f'共有 {total} 个会员没有详细资料')

# 获取已有详细资料的会员数
with_profile = models.UsersProfile.objects.count()
print(f'已有详细资料的会员: {with_profile}')

if total == 0:
    print('所有会员已有详细资料，无需采集')
    sys.exit(0)

success = 0
failed = 0
skipped = 0

for i, user_id in enumerate(users_without_profile):
    try:
        url = f'http://127.0.0.1:8000/api/users/getprofile/{user_id}/'
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read())
        code = data.get('code')
        
        if code == 200:
            success += 1
            print(f'[{i+1}/{total}] 采集成功: user_id={user_id}')
        elif code == 201:
            skipped += 1
            print(f'[{i+1}/{total}] 已存在: user_id={user_id}')
        else:
            failed += 1
            print(f'[{i+1}/{total}] 采集失败: user_id={user_id}, msg={data.get("msg")}')
    except Exception as e:
        failed += 1
        print(f'[{i+1}/{total}] 请求失败: user_id={user_id}, error={e}')
    
    # 每采集10条休息一下，避免触发反爬
    if (i + 1) % 10 == 0:
        print(f'  进度: {i+1}/{total}, 成功={success}, 跳过={skipped}, 失败={failed}')
        time.sleep(1)

print('=' * 60)
print(f'采集完成! 成功={success}, 跳过={skipped}, 失败={failed}')
