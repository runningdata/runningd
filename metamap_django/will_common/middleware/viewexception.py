# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import logging
import traceback

from django.contrib.auth import decorators
from django.contrib.auth import views
from django.http import HttpResponseRedirect

from metamap_django import settings

logger = logging.getLogger('error')


class ViewException():
    def process_exception(self, request, exception):
        logger.error(traceback.format_exc())


class LoginRequire():
    def process_view(self, request, view_func, view_args, view_kwargs):
        logger.info('innnnnnnnnnnnnnnnnnnnnn   login required')
        print('innnnnnnnnnnnnnnnnnnnnn   login required')
        resolved_login_url = decorators.resolve_url('/accounts/login/')
        is_dqms = request.path.startswith('/dqms') and '/rest/' not in request.path
        if is_dqms and not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next' + resolved_login_url)
