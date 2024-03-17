# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/3 13:37
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
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
    # print(type(response.json()['data']['list'][0]))
    dict_data = response.json()
    # print(json.dumps(dict_data, ensure_ascii=False))
    return dict_data


if __name__ == '__main__':
    print(getAnliByPage())
