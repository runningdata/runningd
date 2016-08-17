# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def ifdef(context, var):
    return var in context and context[var] is not None
