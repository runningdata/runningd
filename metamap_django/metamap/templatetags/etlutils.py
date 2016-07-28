# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
from django import template
from django.template import Context, Template

register = template.Library()

@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


if __name__ == '__main__':
    str = '{% load etlutils %}'
    str += '\n {% current_time "%Y-%m-%d %I:%M %p" as nnn %}'
    str += '\n I got a var : {{ nnn }}'
    template = Template(str)
    template.render(Context())