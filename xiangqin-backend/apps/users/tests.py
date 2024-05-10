# from django.test import TestCase

# Create your tests here.
import requests


def get_new_user():
    """
    采集用户信息
    :return:
    """
    base_url = 'http://127.0.0.1:8000/api/users/crawl/?page='

    for i in range(221, 224):
        print(f'开始采集第{i}页')
        requests.get(base_url + str(i))


def get_user_id():
    """
    返回用户id：user_id
    :return:
    """
    url = 'http://127.0.0.1:8000/api/users/list'
    resp = requests.get(url).json()
    # print(resp)

    while True:
        if resp.get('data'):
            for item in resp.get('data'):
                yield item.get('user_id')
        next_page = resp.get('next_page')
        if next_page:
            resp = requests.get(next_page).json()
        else:
            break


def download_user_photo(user_id):
    """
    更新用户详情，并下载用户照片
    :param user_id:
    :return:
    """
    user_profile_url = f"http://127.0.0.1:8000/api/users/getprofile/{user_id}/"

    resp = requests.get(user_profile_url)


def download_users_photo():
    """
    下载数据库中所有用户的照片
    """
    for no, user_id in enumerate(get_user_id()):
        print(f"{no}:{user_id}")
        download_user_photo(user_id)


if __name__ == '__main__':
    # get_new_user()
    download_users_photo()
