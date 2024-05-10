# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/7 22:53
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
import requests

from crawl_data.getHeaders import getHeaders


def getUsersByPage(page):
    """
    采集用户信息，并返回
    :param page: 页码
    :return:
    """
    headers = getHeaders()

    params = {
        'actiontype': 'member',
        'page': page,
        'is_count': '0',
    }

    response = requests.get('https://www.sgjhw.com/pc/love/listrecommend',
                            params=params,
                            headers=headers)

    return response.json()


def getUserOrderByNew(page, is_count=0):
    """

    :param is_count: 当为1时显示总数
    :param page:
    :return:
    """
    headers = getHeaders()

    params = {
        'actiontype': 'member',
        'page': page,
        'is_count': is_count,  # 是否返回总数 1为返回总数，0返回详细
        'orderBy': 'new'
    }

    response = requests.get('https://www.sgjhw.com/pc/love/listrecommend',
                            params=params,
                            headers=headers)

    return response.json()


if __name__ == '__main__':
    print(getUsersByPage(1))
