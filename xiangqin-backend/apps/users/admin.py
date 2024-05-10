import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from . import models


# Register your models here.


@admin.register(models.Users)
class UsersAdminModelAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'user_id',
                    'nickname',
                    'age',
                    'show_gender',
                    'education',
                    'jobs_title',
                    'iscard',
                    'avatar',
                    'getUserProfile',
                    'updatetime']

    list_per_page = 10

    class GenderFilter(admin.SimpleListFilter):
        """
        性别过滤
        """
        title = '性别'  # 过滤标题显示为"以 性别"
        parameter_name = 'gender'  # 过滤器使用的过滤字段

        def lookups(self, request, model_admin):
            """针对字段值设置过滤器的显示效果"""
            return (
                (1, '男'),
                (2, '女'),
            )

        def queryset(self, request, queryset):
            """定义过滤器的过滤动作"""
            if self.value() == "1":
                return queryset.filter(gender=1).all()
            elif self.value() == "2":
                return queryset.filter(gender=2).all()

    list_filter = (GenderFilter, 'iscard', 'isvip')
    search_fields = ['user_id', 'nickname', 'jobs_title']
    sortable_by = ['id', 'age', 'updatetime']
    readonly_fields = ['user_id']
    ordering = ['-updatetime', 'user_id']

    def show_gender(self, obj):
        """

        :param obj:
        :return:
        """
        if obj.gender:
            if obj.gender == 1:
                return '男'
            elif obj.gender == 2:
                return '女'

    def getUserProfile(self, obj):
        """

        :param obj:
        :return:
        """
        return format_html('<a href="{}" target="_blank">获取</a>',
                           reverse('get_user_profile', args=[obj.user_id]))

    def avatar(self, obj):
        """
        显示头像列
        :param obj:
        :return:
        """
        if obj.avatarURL:
            return format_html(f'''
            <a href="{obj.avatarURL.url}" target="blank"> 
                <img src="{obj.avatarURL.url}" width="50" height="50"/>
                </a>
            ''')
        return ""

    avatar.short_description = '头像'
    getUserProfile.short_description = '详情'
    show_gender.short_description = '性别'


@admin.register(models.UsersProfile)
class UsersProfileModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'userID', "age", 'nickname', 'birthday']
    list_display_links = ['id', 'nickname']
    search_fields = ['id', 'nickname', 'memberID__user_id']

    def userID(self, obj):
        if obj.memberID:
            return obj.memberID.user_id

    def birthday(self, obj):
        if obj.BasicInfo:
            return json.loads(obj.BasicInfo)[0][1]

    birthday.short_description = '出生日期'


@admin.register(models.UserProfilePhoto)
class UserProfilePhotoModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'userprofile', 'user_image']
    list_per_page = 10
    search_fields = ['id', 'userprofile__memberID__user_id']

    def user_image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50"/>')
        return ""

    def user_id(self, obj):
        # print(obj)
        return obj.userprofile.memberID.user_id
