# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
import logging
import traceback

from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render

from will_common.utils import dateutils

logger = logging.getLogger('error')


class AccessTracer():
    def process_request(self, request):
        if 'getexeclog' not in request.path:
            print('%s []: user : %s -> url : %s . post params : %s , get params : %s' % (dateutils.now_datetime(), request.user.username, request.path, dict(request.POST), dict(request.GET)))
        return None

class AuthTracer():

    def process_request(self, request):
        is_gene = request.path.startswith(
            '/metamap') and '/rest/' not in request.path and '/generate_job_dag/' not in request.path
        for k, v in settings.PATH_AUTH_DICT.items():
            if not request.user.has_perm(k) and v in request.path and not is_gene:
                message = u'您没有访问此路径的权限'
                return render(request, 'common/message.html', {'message': message})
        return None