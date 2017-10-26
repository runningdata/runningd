# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
from django import template

register = template.Library()


def loggerr(func):
    def day_change(*args, **kwargs):  # 1
        print "Arguments were: %s, %s" % (args, kwargs)
        return func(*args, **kwargs)  # 2

    return day_change


@register.simple_tag
def var(var):
    return var


@register.simple_tag
def now_datetime():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


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


@loggerr
@register.simple_tag
def now_datekey_add(num):
    d = datetime.datetime.now() + datetime.timedelta(days=num)
    return d.strftime('%Y%m%d')


@loggerr
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


@register.simple_tag
def last_month_start(date):
    y, m = get_year_and_month(date)
    if m == 1:  # 如果是1月
        start_date = datetime.date(y - 1, 12, 1)
    else:
        start_date = datetime.date(y, m - 1, 1)
    return start_date.strftime('%Y-%m-%d')


@register.simple_tag
def last_month_end(date):
    y, m = get_year_and_month(date)
    days_ = datetime.date(y, m, 1) - datetime.timedelta(days=1)
    return days_.strftime('%Y-%m-%d')


@register.simple_tag
def current_month_start(date):
    y, m = get_year_and_month(date)
    month_start_dt = datetime.date(y, m, 1)
    return month_start_dt.strftime('%Y-%m-%d')


@register.simple_tag
def current_month_end(date):
    y, m = get_year_and_month(date)
    if m == 12:
        month_end_dt = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
    return month_end_dt.strftime('%Y-%m-%d')


def get_year_and_month(date):
    date1 = datetime.datetime.strptime(date, '%Y-%m-%d')
    y = date1.year
    m = date1.month
    return y, m


status_dic = dict()
status_dic[0] = u'运行中'
status_dic[1] = u'完成'
status_dic[2] = u'失败'


@register.simple_tag
def readable_status(status):
    return status_dic.get(status, u'未知')


schedule_dic = dict()
schedule_dic[0] = u'每天'
schedule_dic[1] = u'每周'
schedule_dic[2] = u'每月'
schedule_dic[3] = u'每季度'
schedule_dic[4] = u'Cron调度'

sche_type_dic = dict()
sche_type_dic[1] = u'ETL'
sche_type_dic[2] = u'EXPORT'
sche_type_dic[3] = u'Hive2Mysql'
sche_type_dic[4] = u'Mysql2Hive'
sche_type_dic[5] = u'SourceApp'
sche_type_dic[6] = u'JarApp'
sche_type_dic[100] = u'调整中'


@register.simple_tag
def readable_schedule(schedule):
    return schedule_dic[schedule]


@register.simple_tag
def readable_sche_type(schedule):
    return sche_type_dic[schedule]


@register.simple_tag
def clean_blood(blood):
    '''
    为了方便mermaid显示，把blood里的@替换为__
    :param blood:
    :return:
    '''
    parentTbl = blood.parentTbl.replace('@', '__').replace('class', 'calss')
    tblName = blood.tblName.replace('@', '__').replace('class', 'calss')
    if blood.current > 0:
        tblName += ';style ' + blood.tblName.replace('@', '__').replace('class',
                                                                        'calss') + ' fill:#f9f,stroke:#333,stroke-width:4px'
    return parentTbl + '-->' + tblName


@register.filter
def is_valid(value):
    if value == 1:
        return '是'
    return '否'


AUTH_DICT = dict()
AUTH_DICT['auth.access_etl'] = u'修改ETL'
AUTH_DICT['auth.access_hadmin'] = u'人员管理'
AUTH_DICT['auth.admin_etl'] = u'管理ETL'


@register.filter
def readable_auth(lis):
    result = u'数据导出'
    for l in lis:
        result += u',' + AUTH_DICT.get(l, u'其他')
    return result

# @register.filter
# def clean_blood(value):
#     return value.replace('@', '__');
