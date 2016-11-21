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
        logger.info('user : %s -> url : %s' % (request.user.username, request.path))
        print('user : %s -> url : %s' % (request.user.username, request.path))
        return None