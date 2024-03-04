from django.db import models


# from apps.images.models import Images


# Create your models here.


class XingFuAnLi(models.Model):
    _id = models.IntegerField('原ID',unique=True)
    comment_num = models.CharField(max_length=100)
    zan_status = models.BooleanField()
    commentstatus = models.BooleanField()
    avatar = models.ImageField(verbose_name='头像', upload_to="images/avatar/")
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    hits = models.CharField(max_length=100)
    commentlist = models.CharField(max_length=100)
    addtime = models.DateField(auto_now=True)
    nickname = models.CharField('昵称', max_length=100)

    class Meta:
        verbose_name = '幸福案例'
        verbose_name_plural = verbose_name



class Images(models.Model):
    """

    """
    image = models.ImageField("图片", null=True, blank=True, upload_to='images/')
    anliInfo = models.ForeignKey(XingFuAnLi, on_delete=models.CASCADE, related_name='imgurl')


