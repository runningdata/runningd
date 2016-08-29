# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metamap_django.settings')

from django.conf import settings  # noqa

app = Celery('metamap')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# bind表示这个函数是一个bound方法，这样就可以访问task类型实例上的属性和方法了
@app.task(bind=True)
def debug_task(self):
    print('Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(
        self.request))
    print('Request: {0!r}'.format(self.request))