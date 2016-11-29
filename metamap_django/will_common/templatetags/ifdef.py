# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_def(context, var):
    result = var in context and context[var] is not None
    return result


@register.simple_tag
def host_clean(status):
    return status[0: len(status) - 5]
