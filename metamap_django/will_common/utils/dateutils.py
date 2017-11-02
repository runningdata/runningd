# -*- coding: utf-8 -*
'''
created by will
常用的日期函数
'''
import datetime, time
from django.utils.timezone import utc
from django.utils.timezone import localtime

def now_datetime():
    return time.strftime("%Y%m%d%H%M%S")


def now_date():
    return time.strftime("%Y-%m-%d")


def now_datekey():
    return time.strftime("%Y%m%d")

def days_before_now(date):
    result = datetime.datetime.now() - datetime.datetime.strptime(date, "%Y%m%d")
    return result.days

def days_ago(days):
    dat = datetime.datetime.now() + datetime.timedelta(days=days)
    return dat.strftime("%Y-%m-%d")

def days_ago_key(days):
    dat = datetime.datetime.now() + datetime.timedelta(days=days)
    return dat.strftime("%Y%m%d")

def format_day(time):
    return time.strftime("%Y%m%d%H%M%S")


def format_dbday(time):
    return localtime(time.replace(tzinfo=utc)).strftime("%Y-%m-%d %H:%M:%S")