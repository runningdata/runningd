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
