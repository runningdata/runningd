# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''
import logging
import traceback

from will_common.utils import dateutils

logger = logging.getLogger('error')


class AccessTracer():
    def process_request(self, request):
        print('%s []: user : %s -> url : %s . post params : %s , get params : %s' % (dateutils.now_datetime(), request.user.username, request.path, dict(request.POST), dict(request.GET)))
        return None