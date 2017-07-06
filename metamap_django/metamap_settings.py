# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

import os

print('gunicorn config is running....')

bind = "0.0.0.0:8088"
# worker_class = "eventlet"
worker_class = "gevent"
workers = 4
# workers = multiprocessing.cpu_count() * 2 + 1
pidfile = '/tmp/metamap_gunicorn.pid'
# accesslog = '/tmp/gunicorn_access.log'
errorlog = '/tmp/metamap_gunicorn_error.log'
loglevel = 'info'
capture_output = True
timeout=600
proc_name = 'will\'s metamap'
daemon = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metamap.config.prod")
