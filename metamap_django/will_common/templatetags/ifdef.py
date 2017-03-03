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

@register.simple_tag(takes_context=True)
def get_verbose(context, field):
    return context['obj']._meta.get_field_by_name(field)[0].verbose_name
