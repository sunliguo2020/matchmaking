from django.db import models
from datetime import date

# from apps.images.models import Images


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
        
    def __str__(self):
        return str(self.id)


class Images(models.Model):
    """
    幸福案例中某个实例中要保存的图片。

    """
    image = models.ImageField("图片", null=True, blank=True, upload_to='images/anli/')
    anliInfo = models.ForeignKey(XingFuAnLi, on_delete=models.CASCADE, related_name='imgurl')
