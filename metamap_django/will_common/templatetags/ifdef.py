# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
import json

from django import template
from kombu.serialization import pickle

register = template.Library()


@register.simple_tag(takes_context=True)
def has_def(context, var):
    result = var in context and context[var] is not None
    return result


@register.simple_tag
def host_clean(status):
    return status[0: len(status) - 5]


@register.simple_tag
def get_from_dict(dict, level_1):
    return dict[level_1]


@register.simple_tag
def get_date_num(db_dict, date):
    return db_dict.get(date, 0)


@register.simple_tag(takes_context=True)
def get_verbose(context, field):
    return context['obj']._meta.get_field_by_name(field)[0].verbose_name


@register.simple_tag
def get_celery_taskname(msg):
    m = json.loads(msg)
    body_encoding = m[0]['properties']['body_encoding']
    body = pickle.loads(m[0]['body'].decode(body_encoding))
    return body


@register.simple_tag
def get_celery_taskname2(msg):
    m = json.loads(msg)
    body_encoding = m['properties']['body_encoding']
    body = 'problem...'
    try:
        body = pickle.loads(m['body'].decode(body_encoding))
    except Exception, e:
        print('result is %s ' % m['body'])
    return body


@register.filter
def extract_str_dict(value, key):
    return eval(value).get(key, "has no name yet")


@register.filter
def readable_task_queue(value):
    ss = value.split('@')
    if len(ss) == 2:
        return ss[0].replace('will_', '')
    else:
        return value
