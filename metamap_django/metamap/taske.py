# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from __future__ import absolute_import

import logging
import subprocess

from celery import shared_task
from django.utils import timezone

from metamap.models import ETL, Executions
from metamap.utils import enums

logger = logging.getLogger('django')


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def exec_etl(command, log):
    p = subprocess.Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True,
                         universal_newlines=True)
    p.wait()
    returncode = p.returncode
    execution = Executions.objects.get(logLocation=log)
    execution.end_time = timezone.now()
    logger.info('%s return code is %d' % (command, returncode))
    if returncode == 0:
        execution.status = enums.EXECUTION_STATUS.DONE
    else:
        execution.status = enums.EXECUTION_STATUS.FAILED
    execution.save()
    return ETL.objects.all()

@shared_task
def xsum(numbers):
    return sum(numbers)
