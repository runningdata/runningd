# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

import os

print('gunicorn config is running....')

bind = "0.0.0.0:8099"
worker_class = "eventlet"
workers = 4
# workers = multiprocessing.cpu_count() * 2 + 1
pidfile = '/tmp/metamap_beta_gunicorn.pid'
# accesslog = '/tmp/gunicorn_access.log'
errorlog = '/tmp/metamap_beta_gunicorn_error.log'
loglevel = 'info'
capture_output = True
timeout=600
proc_name = 'will\'s metamap beta'
daemon = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metamap.config.beta")
