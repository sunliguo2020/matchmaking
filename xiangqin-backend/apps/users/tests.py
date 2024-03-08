from django.test import TestCase

# Create your tests here.
import requests

base_url = 'http://127.0.0.1:8000/api/users/crawl/?page='

for i in range(215, 216):
    print(f'开始采集第{i}页')
    requests.get(base_url + str(i))
