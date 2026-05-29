from django.db import models
from datetime import date
from comm.db import BaseModel

# Create your models here.


class XingFuAnLi(models.Model):
    _id = models.IntegerField('原ID', unique=True)
    comment_num = models.CharField(max_length=100)
    zan_status = models.BooleanField()
    commentStatus = models.BooleanField()
    avatar = models.ImageField(verbose_name='头像', upload_to="images/avatar/")
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    hits = models.CharField(max_length=100)
    commentlist = models.CharField(max_length=100)
    addtime = models.DateField(default=date.today)
    nickname = models.CharField('昵称', max_length=100)

    class Meta:
        verbose_name = '幸福案例'
        verbose_name_plural = verbose_name
        ordering = ['-addtime']
        
    def __str__(self):
        return str(self.id)


class Images(models.Model):
    """
    幸福案例中某个实例中要保存的图片。

    """
    image = models.ImageField("图片", null=True, blank=True, upload_to='images/anli/')
    anliInfo = models.ForeignKey(XingFuAnLi, on_delete=models.CASCADE, related_name='imgurl')

    class Meta:
        verbose_name = '幸福案例图片'
        verbose_name_plural = verbose_name


class Activity(models.Model):
    """
    相亲活动
    """
    aid = models.IntegerField('活动ID', unique=True)
    title = models.CharField('活动标题', max_length=200)
    address = models.CharField('活动地址', max_length=200, blank=True, default='')
    cover_img = models.URLField('封面图片', max_length=500, blank=True, default='')
    big_img = models.URLField('大图', max_length=500, blank=True, default='')
    date_desc = models.CharField('活动日期描述', max_length=100, blank=True, default='')
    date_act = models.CharField('活动日期', max_length=100, blank=True, default='')
    price = models.CharField('价格', max_length=20, blank=True, default='')
    vip_price = models.CharField('VIP价格', max_length=20, blank=True, default='')
    money_sex1 = models.CharField('男价格', max_length=20, blank=True, default='')
    money_sex2 = models.CharField('女价格', max_length=20, blank=True, default='')
    location = models.CharField('位置', max_length=200, blank=True, default='')
    is_over = models.BooleanField('是否结束', default=False)
    over_content = models.TextField('结束内容', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '相亲活动'
        verbose_name_plural = verbose_name
        ordering = ['-aid']

    def __str__(self):
        return self.title
