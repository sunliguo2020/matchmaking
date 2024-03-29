# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/3 13:37
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
import pprint

import jsonpath
import requests

from crawl_data.getHeaders import getHeaders


def getAnliByPage(page=1):
    """
    获取幸福案例
    :param page:
    :return:
    """
    url = 'https://www.sgjhw.com/pc/love/tuodan'
    params = {
        'actiontype': 'tuodan',
        'page': page,
    }

    response = requests.get(url,
                            params=params,
                            headers=getHeaders())
    dict_data = response.json()
    # 获取案例数目
    count = jsonpath.jsonpath(dict_data, '$..count')
    if count:
        count = count[0]
        print(count)

    return dict_data


if __name__ == '__main__':
    pprint.pp(getAnliByPage())
