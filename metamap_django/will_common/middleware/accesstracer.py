# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
import logging
import traceback

logger = logging.getLogger('error')


class AccessTracer():
    def process_request(self, request):
        print('user : %s -> url : %s . post params : %s , get params : %s' % (request.user.username, request.path, dict(request.POST), dict(request.GET)))
        return None