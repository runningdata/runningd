# -*- coding: utf-8 -*
import logging

from will_common.models import UserProfile


def add_current_user(obj, attr,request):
    if hasattr(obj, attr):
        setattr(obj, attr, request.user.userprofile)

def add_current_creator(obj,request):
    add_current_user(obj, 'creator', request)