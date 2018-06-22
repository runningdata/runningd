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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class AccessTracer():
    def process_request(self, request):
        if 'getexeclog' not in request.path:
            if request.method == 'GET':
                print('[%s]: %s @ %s: %s -> url : %s . , get params : %s' % (
                dateutils.now_datetime(), request.user.username, get_client_ip(request), request.method, request.path, dict(request.GET)))

            elif request.method == 'POST':
                if 'nosecure' not in request.path:
                    print('[%s]: %s @ %s %s -> url : %s . post params : %s' % (
                    dateutils.now_datetime(), request.user.username, get_client_ip(request), request.method, request.path, dict(request.POST)))
                else:
                    print('[%s]: %s @ %s %s -> url : %s . post params : %s' % (
                        dateutils.now_datetime(), request.user.username, get_client_ip(request), request.method,
                        request.path, 'push thing'))
            else:
                print('[%s]: %s @ %s %s -> url : %s . post params : %s , get params : %s' % (
                dateutils.now_datetime(), request.user.username, get_client_ip(request), request.method, request.path, dict(request.POST), dict(request.GET)))
        return None


class AuthTracer():
    def process_request(self, request):
        is_filelist = request.path.startswith(
            '/metamap/rest/exports')
        is_gene = '/generate_job_dag/' in request.path or 'push_msg' in request.path
        if is_filelist or is_gene:
            return None

        for k, v in settings.PATH_AUTH_DICT.items():
            if not request.user.has_perm(k) and request.path.startswith(v):
                message = u'您没有访问此路径的权限'
                return render(request, 'common/message.html', {'message': message})
        return None
