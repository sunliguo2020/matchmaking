# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/8 21:57
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from fake_useragent import UserAgent
from crawl_data.hashtoken import header_hashtoken


def getHeaders():
    """
    返回带hashtoken的请求头
    :return:
    """
    ua = UserAgent()
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.sgjhw.com/web/member/list',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'User-Agent':  ua.random,
        'hashtoken': header_hashtoken(),
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    return headers


if __name__ == '__main__':
    print(getHeaders())
