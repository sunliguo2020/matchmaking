# -*- coding: utf-8 -*-
"""
 @Time : 2024/3/5 20:18
 @Author : sunliguo
 @Email : sunliguo2006@qq.com
"""
from io import BytesIO

import requests
from django.core.files.base import ContentFile


def save_remote_image_to_instance(remote_image_url, instance):
    """
    保存远程图片到模型类实例中
    :param remote_image_url:
    :param instance:
    :return:

    """
    # 发送GET请求获取远程图片
    response = requests.get(remote_image_url, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BytesIO处理二进制数据
        image_content = BytesIO(response.content)

        # 创建一个ContentFile对象，它可以被Django的ImageField接受
        image_file = ContentFile(image_content.getvalue())

        # 将ContentFile对象赋值给模型的ImageField
        instance.image_field = image_file  # 替换为你的ImageField名称

        # 保存模型实例，这将触发ImageField的保存
        instance.save()
    else:
        print(f'Failed to download image from {remote_image_url}')


def get_remote_image_content_file(remote_image_url):
    """

    :param remote_image_url:
    :return:
    """
    # 发送GET请求获取远程图片
    response = requests.get(remote_image_url, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BytesIO处理二进制数据
        image_content = BytesIO(response.content)

        # 创建一个ContentFile对象，它可以被Django的ImageField接受
        image_file = ContentFile(image_content.getvalue())

        return image_file
    else:
        print(f'Failed to download image from {remote_image_url}')
