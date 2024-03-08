from django.contrib import admin
from django.utils.html import format_html

# Register your models here.

from . import models


@admin.register(models.XingFuAnLi)
class XingFuAnLiAdmin(admin.ModelAdmin):
    list_display = ['id', '_id', 'title', 'content', 'avatar_tag', 'imgurl']
    list_per_page = 10
    def avatar_tag(self, obj):
        """
        显示头像列图片
        :param obj:
        :return:
        """
        if obj.avatar:
            return format_html(f'<img src="{obj.avatar.url}" width="50" height="50"/>')
        return ""

    def imgurl(self, obj):
        """
        显示相关图片
        :param obj:
        :return:
        """
        html_str = ''
        img_objs = models.Images.objects.filter(anliInfo_id__exact=obj.id)
        if img_objs:
            # imgurl = [i for i in img_objs.values_list('image', flat=True)]
            # return imgurl
            for i in img_objs:
                html_str += f"<img src='{i.image.url}' width='50' height='50'/>"

            return format_html(html_str)


@admin.register(models.Images)
class AnliImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_tag', 'anliInfo']
    list_per_page = 10

    def image_tag(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="100" height="100"/>')
        else:
            return ""
