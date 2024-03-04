from django.contrib import admin

# Register your models here.

from . import models


@admin.register(models.XingFuAnLi)
class XingFuAnLiAdmin(admin.ModelAdmin):
    list_display = ['id', '_id', 'title', 'content', 'imgurl']

    def imgurl(self, obj):
        img_objs = models.Images.objects.filter(anliInfo_id__exact=obj.id)
        if img_objs:
            imgurl = [i for i in img_objs.values_list('image', flat=True)]
            return imgurl
        return
