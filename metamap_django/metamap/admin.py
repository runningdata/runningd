#coding:utf-8

from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your models here.
def submit_application(modeladmin, request, queryset):
    return ''

submit_application.short_description = "提交申请"

class ETLAdmin(admin.ModelAdmin):
    actions = [submit_application]

    def get_app_url(self, obj):  # 显示app的版本持续集成状态页面的链接
        return format_html(u'<a href="http://app.aliyun.com/%s/%s">状态</a>' % (obj.appname, obj.version))

    get_app_url.short_description = '持续集成状态'

    readonly_fields = ('onSchedule',)
    list_display = ('query', 'name', 'preSql')
    search_fields = ('name',)
    list_filter = ('valid',)

admin.site.register(TblBlood)
admin.site.register(ETL, ETLAdmin)
admin.site.register(Executions)
admin.site.register(Meta)