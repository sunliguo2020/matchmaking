import json

from django.test import TestCase

# Create your tests here.
json_str = '''
{
    "id": 330092,
    "age": "28岁",
    "height": "170cm",
    "weight": "55kg",
    "avatarURL": "https://x96-img.xindongyun.cn/appu330092d6c7312024030414384693575oq7wls.png?imageView2/1/w/204/h/248/q/85",
    "city": "潍坊市",
    "education": "大专",
    "gender": 1,
    "marriage": "未婚",
    "nickname": "灵魂操控者",
    "objectID": 330092,
    "jobs_title": "生产/制造",
    "online": 0,
    "city_name": "潍坊市,寿光市,洛城街道",
    "hometown_name": "山东省,潍坊市,寿光市,洛城街道",
    "flagList": {
        "isvip": 0,
        "iscard": 1
    },
    "isvip": 0,
    "iscard": 1,
    "f_text": [
        "自驾游",
        "旅行",
        "恋爱以结婚为目的"
    ],
    "updatetime": 1709817177,
    "infoStatus": {
        "info": "审核通过",
        "ischeck": 1
    },
    "placedtop": 0,
    "revenue": "5千~8千",
    "ismeet": 0
}'''

json_obj = json.loads(json_str)
print(type(json_obj.get('f_text')))