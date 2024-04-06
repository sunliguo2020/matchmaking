# from django.test import TestCase

# Create your tests here.
import requests
# from apps.users import models


def get_new_user():
    base_url = 'http://127.0.0.1:8000/api/users/crawl/?page='

    for i in range(200, 222):
        print(f'开始采集第{i}页')
        requests.get(base_url + str(i))


def download_user_photo():
    for item in models.Users.objects.all():
        print(item.id)


if __name__ == '__main__':
    # download_user_photo()
    get_new_user()
