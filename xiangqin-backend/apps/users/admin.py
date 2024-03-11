import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from . import models


# Register your models here.

@admin.register(models.Users)
class UsersAdminModelAdmin(admin.ModelAdmin):
    list_display = ['id',
                    '_id',
                    'nickname',
                    'age',
                    'show_gender',
                    'education',
                    'jobs_title',
                    'avatar',
                    'getUserProfile']
    list_per_page = 10
    # list_filter = ['show_gender']
    search_fields = ['_id', 'nickname', 'jobs_title']
    sortable_by = ['id', 'age']
    readonly_fields = ['_id']
    ordering = ['-updatetime', '_id']

    def show_gender(self, obj):
        if obj.gender:
            if obj.gender == 1:
                return '男'
            elif obj.gender == 2:
                return '女'

    def getUserProfile(self, obj):
        print(obj)
        return format_html('<a href="{}" target="_blank">获取</a>',
                           reverse('get_user_profile', args=[obj._id]))

    def avatar(self, obj):
        if obj.avatarURL:
            return format_html(f'<img src="{obj.avatarURL.url}" width="50" height="50"/>')
        return ""

    avatar.short_description = '头像'
    getUserProfile.short_description = '详情'
    show_gender.short_description = '性别'


@admin.register(models.UsersProfile)
class UserProfileModelAdmin(admin.ModelAdmin):
    list_display = ['id', "age", 'nickname', 'birthday']
    list_display_links = ['id', 'nickname']

    # pass
    def birthday(self, obj):
        if obj.BasicInfo:
            return json.loads(obj.BasicInfo)[0][1]

    birthday.short_description = '出生日期'
