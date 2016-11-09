# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import logging
import os
import subprocess
import traceback

from celery import shared_task, task
from django.utils import timezone

from dqms.models import DqmsCheckInst, DqmsCheck

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/dqms/'



@shared_task
def exec_dqms(task_id):
    check = DqmsCheck.objects.get(pk=task_id)
    chk_inst = DqmsCheckInst.objects.create(chk=check, case_num=check.cases.count())
    chk_inst.save()
    try:
        for case in check.cases.all():
            print('processing %s ' % case.case_name)
        chk_inst.end_time = timezone.now()
        chk_inst.save()
    except Exception, e:
        logger.error('ERROR: %s' % traceback.format_exc())
        chk_inst.end_time = timezone.now()
        chk_inst.save()

