from django.db import models


# Create your models here.
class Users(models.Model):
    _id = models.IntegerField()
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
