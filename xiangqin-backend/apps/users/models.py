from django.core.files.storage import default_storage
from django.db import models


# Create your models here.
class Users(models.Model):
    """
    会员基本信息
    """
    user_id = models.IntegerField('用户ID', unique=True)
    age = models.CharField('年龄', max_length=10)
    height = models.CharField('身高', max_length=10)
    weight = models.CharField('体重', max_length=10)
    avatarURL = models.ImageField('头像', upload_to='images/avatar/')
    city = models.CharField('城市', max_length=10)
    education = models.CharField('教育', max_length=10)
    gender = models.SmallIntegerField('性别')
    marriage = models.CharField('婚否', max_length=10)
    nickname = models.CharField('昵称', max_length=50)
    objectID = models.IntegerField()
    jobs_title = models.CharField('职业', max_length=10)
    online = models.IntegerField()
    city_name = models.CharField('城市名', max_length=10)
    hometown_name = models.CharField('家乡', max_length=10)
    flagList = models.JSONField()
    isvip = models.SmallIntegerField()
    iscard = models.SmallIntegerField()
    f_text = models.CharField(max_length=200)
    updatetime = models.DateTimeField()
    infoStatus = models.CharField(max_length=50)
    placedtop = models.SmallIntegerField()
    revenue = models.CharField('收入', max_length=20)
    ismeet = models.SmallIntegerField()

    class Meta:
        verbose_name = '会员信息'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        # 判断头像文件是否已经存在
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """

        :param using:
        :param keep_parents:
        """
        # 在删除模型对象之前删除文件
        # 删除ImageField关联的文件
        image_path = self.avatarURL.path
        print(f'avatarURL文件{image_path}')
        if default_storage.exists(image_path):
            default_storage.delete(image_path)
        # if self.avatarURL:
        #     print('准备删除头像文件')
        #     self.avatarURL.delete(save=False)
        #     # 调用父类的delete方法完成实际的删除操作
        super().delete(using=None, keep_parents=False)

    def __str__(self):
        return self.nickname


class UsersProfile(models.Model):
    """
    会员详细信息
    """
    """
{
    "nickname": "桃",
    "showValidateIDCardFlag": 0,
    "workCityString": "潍坊市",
    "age": 25,
    "gender": 2,
    "isedu": 0,
    "iscar": 0,
    "ishouse": 0,
    "isvip": 1,
    "iscard": 1,
    "BasicInfo": [
        [
            "出生年月",
            "1999-3"
        ],
        [
            "身高",
            "167cm"
        ],
        [
            "体重",
            "48Kg"
        ],
        [
            "学历",
            "本科"
        ],
        [
            "婚姻状况",
            "未婚"
        ],
        [
            "户籍地",
            "山东省,潍坊市,寿光市,稻田镇"
        ],
        [
            "现居地址",
            "山东省,潍坊市,寿光市,圣城街道"
        ],
        [
            "买房情况",
            "和家人同住"
        ],
        [
            "买车情况",
            "未买车"
        ],
        [
            "何时结婚",
            "时机成熟就结婚"
        ]
    ],
    "DetailInfo": [
        [
            "职业",
            "教师"
        ],
        [
            "月收入",
            "5千~8千"
        ]
    ],
    "ObjectInfo": [
        [
            "年龄",
            "24-27岁"
        ],
        [
            "身高",
            "175cm以上"
        ],
        [
            "学历",
            "本科及以上"
        ],
        [
            "婚姻状况",
            "仅限未婚"
        ],
        [
            "月收入",
            "5千以上"
        ],
        [
            "是否接受对方有小孩",
            "不接受"
        ]
    ],
    "memberID": 1179833,
    "vnums": 0,
    "showinfo": 1,
    "mate": "",
    "f_text": [
        "慢热",
        "真诚靠谱",
        "善解人意"
    ],
    "pull_nums": 0,
    "imkey": 0,
    "revenue_type": 1,
    "ismeet": 0,
    "userlimit": 0,
    "basic": {
        "addtime_text": "",
        "updatatime_text": "",
        "height": "167cm",
        "weight": "48Kg",
        "edu": "本科",
        "marriage": "未婚",
        "hometown_name": "山东省,潍坊市,寿光市,稻田镇",
        "house": "和家人同住",
        "studyabroad": "教师",
        "revenue": "5千~8千"
    },
    "basicInfo": [
        "1999-3",
        "山东省,潍坊市,寿光市,稻田镇",
        "山东省,潍坊市,寿光市,圣城街道"
    ],
    "tag_true": [
        "整洁干净",
        "有责任心",
        "孝敬父母",
        "懂得尊重",
        "不冷暴力"
    ],
    "thumb": [],
    "avatarURL": {
        "b": "https://x96-img.xindongyun.cn/h5u1179833dd6a482023012510390328828wnax7k.jpg",
        "m": "https://x96-img.xindongyun.cn/h5u1179833dd6a482023012510390328828wnax7k.jpg?imageView2/1/w/300/h/366/q/85"
    },
    "giftCount": 3,
    "gift": [
        {
            "giftID": 1540,
            "giftIcon": "http://img2.inke.cn/MTQ5ODQ3NTk3NzEyMSM5MDgjanBn.jpg",
            "giftName": "守护之心",
            "giftPrice": 1,
            "isFree": false,
            "isNew": false,
            "num": 1
        },
        {
            "giftID": 1539,
            "giftIcon": "http://img2.inke.cn/MTUwMDQ2NjY4NjA4MSMxNjQjanBn.jpg",
            "giftName": "玛莎拉蒂",
            "giftPrice": 88,
            "isFree": false,
            "isNew": false,
            "num": 1
        },
        {
            "giftID": 1533,
            "giftIcon": "http://img2.inke.cn/MTUxMzA0NjgyMTA1OSM2OTMjanBn.jpg",
            "giftName": "浪漫秋千",
            "giftPrice": 58,
            "isFree": false,
            "isNew": false,
            "num": 1
        }
    ],
    "isFollowing": false,
    "userinfo": {
        "memberID": 0,
        "is_card": 0,
        "vipid": 0,
        "viptime": 0,
        "imkey": 0,
        "goldNum": 0,
        "sex": 0,
        "ischeck": 4,
        "isedu": 0,
        "iscar": 0,
        "ishouse": 0
    },
    "hn": [],
    "userinfocheck": {
        "basic_check": 0,
        "want_check": 0
    },
    "client": 7,
    "seo": {
        "title": "167cm 48Kg 本科 未婚",
        "description": "寿光相亲网，寿光本地真实靠谱相亲平台！只征婚不交友！",
        "keywords": "潍然心动·寿光相亲网",
        "imgUrl": "https://x96-img.xindongyun.cn/h5u1179833dd6a482023012510390328828wnax7k.jpg?imageView2/1/w/200/q/85"
    },
    "isfull": false,
    "step": 1
}
"""

    nickname = models.CharField('昵称', max_length=50)
    showValidateIDCardFlag = models.SmallIntegerField(default=0)
    workCityString = models.CharField('工作城市', max_length=50)
    age = models.IntegerField('年龄')
    gender = models.SmallIntegerField()
    isedu = models.SmallIntegerField()
    iscar = models.SmallIntegerField()
    ishouse = models.SmallIntegerField()
    isvip = models.SmallIntegerField()
    iscard = models.SmallIntegerField()
    BasicInfo = models.CharField('详细资料', max_length=200)
    DetailInfo = models.CharField('其他资料', max_length=100)
    ObjectInfo = models.CharField('择偶标准', max_length=200)
    # 关联Users主键
    memberID = models.OneToOneField(to=Users, on_delete=models.CASCADE)
    vnums = models.SmallIntegerField()
    showinfo = models.SmallIntegerField()
    mate = models.CharField(max_length=100)
    # 我的性格
    f_text = models.CharField('兴趣爱好', max_length=100)
    pull_nums = models.SmallIntegerField()
    imkey = models.SmallIntegerField()
    revenue_type = models.SmallIntegerField()
    ismeet = models.SmallIntegerField()
    userlimit = models.SmallIntegerField()
    basic = models.JSONField()
    basicInfo2 = models.CharField(max_length=100)
    tag_true = models.CharField('理想中的TA', max_length=100)
    # 个人照片原始地址
    thumb = models.CharField(max_length=100)
    avatarURL = models.JSONField('头像')
    giftCount = models.IntegerField('礼物数')
    gift = models.CharField(max_length=100)
    isFollowing = models.BooleanField()
    userinfo = models.JSONField()
    hn = models.CharField(max_length=100)
    userinfocheck = models.JSONField()
    client = models.IntegerField()
    seo = models.JSONField()
    isfull = models.BooleanField()
    step = models.IntegerField()

    class Meta:
        verbose_name = '会员详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname


class UserProfilePhoto(models.Model):
    """
    保存用户上传的照片
    来自于UsersProfile中的thumb字段
    """
    image = models.ImageField("图片", null=True, blank=True, upload_to='images/user_photo/')
    userprofile = models.ForeignKey(to=UsersProfile, on_delete=models.CASCADE, to_field='memberID')

    class Meta:
        verbose_name = '会员相册'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.userprofile.nickname + self.image.name
