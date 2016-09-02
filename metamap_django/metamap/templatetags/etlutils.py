# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
from django import template

register = template.Library()


@register.simple_tag
def var(var):
    return var


@register.simple_tag
def now_datetime():
    return datetime.datetime.now().strftime('%Y%m%d%I%M%S')


@register.simple_tag
def now_datekey():
    return datetime.datetime.now().strftime('%Y%m%d')


@register.simple_tag
def now_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


@register.simple_tag
def date2datekey(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')


@register.simple_tag
def datekey2date(datekey):
    return datetime.datetime.strptime(datekey, '%Y%m%d').strftime('%Y-%m-%d')


@register.simple_tag
def now_datekey_add(num):
    d = datetime.datetime.now() + datetime.timedelta(days=num)
    return d.strftime('%Y%m%d')


@register.simple_tag
def now_date_add(num):
    d = datetime.datetime.now() + datetime.timedelta(days=num)
    return d.strftime('%Y-%m-%d')


@register.simple_tag
def current_datekey_add(datekey, num):
    '''
    传入datekey和要添加的天数
    '''
    d = datetime.datetime.strptime(datekey, '%Y%m%d') + datetime.timedelta(days=num)
    return d.strftime('%Y%m%d')


@register.simple_tag
def current_date_add(date, num):
    d = datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=num)
    return d.strftime('%Y-%m-%d')


status_dic = dict()
status_dic[0] = u'运行中'
status_dic[1] = u'完成'
status_dic[2] = u'失败'


@register.simple_tag
def readable_status(status):
    return status_dic[status]


schedule_dic = dict()
schedule_dic[0] = u'每天'
schedule_dic[1] = u'每周'
schedule_dic[2] = u'每月'
schedule_dic[3] = u'每季度'
schedule_dic[4] = u'Cron调度'


@register.simple_tag
def readable_schedule(schedule):
    return schedule_dic[schedule]


@register.filter
def is_valid(value):
    if is_valid == 1:
        return '是'
    return '否'


@register.filter
def clean_blood(value):
    return value.replace('@', '__');
