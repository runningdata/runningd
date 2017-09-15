# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

import os

print('running_alert gunicorn config is running....')

bind = "0.0.0.0:10099"
worker_class = "eventlet"
workers = 2
pidfile = '/tmp/running_alert_gunicorn.pid'
# accesslog = '/tmp/gunicorn_access.log'
errorlog = '/tmp/running_alert_gunicorn_error.log'
loglevel = 'info'
capture_output = True
timeout = 600
proc_name = 'will\'s running_alert'
daemon = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "running_alert.config.prod")
