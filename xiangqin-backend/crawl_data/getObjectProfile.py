# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/10 14:10
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""

import requests

from crawl_data.getHeaders import getHeaders


def getObjectProfile(id):
    """

    :param id:
    :return:
    """
    params = {
        'actiontype': 'member',
        'id': id,
    }

    response = requests.get('https://www.sgjhw.com/pc/love/getObjectProfile',
                            params=params,
                            headers=getHeaders())
    return response.json()


if __name__ == '__main__':
    print(getObjectProfile('1186282'))
