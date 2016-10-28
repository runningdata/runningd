# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import logging
import traceback

logger = logging.getLogger('error')


class ViewException():
    def process_exception(self, request, exception):
        logger.error(traceback.format_exc())

    