# -*- coding: utf-8 -*-
"""
采集 menutype=2 接口的所有数据，使用 lasttime 游标翻页

lasttime 翻页机制分析：
- 不传 lasttime：返回最新的数据，返回的 lasttime = 最大updatetime + 1
- 传 lasttime：返回 updatetime 小于等于该时间戳的数据
- 翻页方式：用该页中最小 updatetime 作为下一页的 lasttime
- hasMore=true 表示还有更早的数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'xiangqin.settings'

import django
django.setup()

import urllib.request
import json

from crawl_data.getUsers import getUsersByPage

lasttime = None
page = 1
total_new = 0

print('开始采集 menutype=2 接口数据...')
print('=' * 60)

while True:
    # 获取数据
    r = getUsersByPage(1, menutype=2, lasttime=lasttime)
    items = r.get('data', {}).get('list', [])

    if not items:
        print(f'第{page}次请求: 没有数据')
        break

    ids = [i['id'] for i in items]
    updatetimes = [i['updatetime'] for i in items]
    print(f'第{page}次请求: {len(ids)}条, ids={ids[:5]}...')
    print(f'  updatetime范围: {min(updatetimes)} ~ {max(updatetimes)}')

    # 获取下一页需要的lasttime（最小updatetime）
    new_lasttime = min(updatetimes)
    hasMore = r.get('data', {}).get('hasMore')
    print(f'  下一页lasttime={new_lasttime}, hasMore={hasMore}')

    # 通过API采集到数据库
    params = f'page=1&menutype=2'
    if lasttime:
        params += f'&lasttime={lasttime}'

    try:
        resp = urllib.request.urlopen(f'http://127.0.0.1:8000/api/users/crawl/?{params}', timeout=10)
        data = json.loads(resp.read())
        print(f'  结果: {data.get("msg")}')
        total_new += data.get('data', {}).get('created', 0)
    except Exception as e:
        print(f'  采集失败: {e}')

    # 更新lasttime用于下一页
    lasttime = new_lasttime
    page += 1

    if not hasMore:
        print('hasMore=False, 停止翻页')
        break

print('=' * 60)
print(f'采集完成! 共请求{page-1}次, 新增{total_new}条')
