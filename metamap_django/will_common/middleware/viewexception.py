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
from django.shortcuts import render

logger = logging.getLogger('error')


class ViewException():
    def process_exception(self, request, exception):
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        if hasattr(exception, 'err_stack'):
            return render(request, 'common/message.html',
                          {'message': exception.message, 'err_stack': exception.err_stack})
        return render(request, 'common/message.html',
                      {'message': exception.message, 'err_stack': traceback.format_exc()})


class LoginRequire():
    def process_view(self, request, view_func, view_args, view_kwargs):
        resolved_login_url = decorators.resolve_url('/accounts/login/')
        is_dqms = request.path.startswith('/dqms') and '/rest/' not in request.path
        is_alert = request.path.startswith('/alert') and '/rest/' not in request.path
        is_gene = request.path.startswith(
            '/metamap') and '/rest/' not in request.path and '/generate_job_dag/' not in request.path
        is_export = request.path.startswith('/export')
        is_test = request.path.endswith('test/') or 'push_msg' in request.path

        if not is_test:
            if (is_dqms or is_gene or is_export or is_alert) and not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/?next' + resolved_login_url)
