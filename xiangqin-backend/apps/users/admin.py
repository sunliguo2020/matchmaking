from django.contrib import admin
from django.utils.html import format_html

from . import models


# Register your models here.

@admin.register(models.Users)
class UsersAdminModelAdmin(admin.ModelAdmin):
    list_display = ['id', '_id', 'nickname', 'age', 'education', 'jobs_title', 'avatar']
    list_per_page = 10
    # list_filter = ['education']
    search_fields = ['_id', 'nickname', 'jobs_title']
    sortable_by = ['id', 'age']
    readonly_fields = ['_id']
    ordering = ['-updatetime', '_id']

    def avatar(self, obj):
        if obj.avatarURL:
            return format_html(f'<img src="{obj.avatarURL.url}" width="50" height="50"/>')
        return ""

    avatar.short_description = '头像'

    class Meta:
        js = ('static/custom.js')
        css = {
            "all": ("static/custom.css")
        }
