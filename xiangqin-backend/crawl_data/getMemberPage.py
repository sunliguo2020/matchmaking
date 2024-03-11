# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/8 21:59
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
import requests

from crawl_data.getHeaders import getHeaders


def getMemberCount():
    """
    返回会员数
    :return:
    """
    headers = getHeaders()

    params = {
        'actiontype': 'memberPage',
        'page': 1,
        'is_count': '1',
        'orderBy': 'new'
    }

    response = requests.get('https://www.sgjhw.com/pc/love/listrecommend',
                            params=params,
                            headers=headers)

    resp_json = response.json()

    if resp_json.get('code') == 200:
        return resp_json.get('data').get('count')
    else:
        return


if __name__ == '__main__':
    print(getMemberCount())
