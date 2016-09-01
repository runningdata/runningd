# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import logging
import subprocess

from celery import shared_task, task
from django.utils import timezone

from metamap.models import ETL, Executions
from metamap.utils import enums

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task
def xx():
    return 'sdfsdf'


@shared_task
def add(x, y):
    return x + y


@shared_task
def exec_etl(command, log):
    execution = Executions.objects.get(logLocation=log)
    execution.end_time = timezone.now()
    try:
        p = subprocess.Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True,
                             universal_newlines=True)
        p.wait()
        returncode = p.returncode
        logger.info('%s return code is %d' % (command, returncode))
        if returncode == 0:
            execution.status = enums.EXECUTION_STATUS.DONE
        else:
            execution.status = enums.EXECUTION_STATUS.FAILED
    except Exception, e:
        logger.error(e)
        execution.status = enums.EXECUTION_STATUS.FAILED
    execution.save()


@shared_task
def exec_etl_cli(command, header, result):
    print 'command is ', command
    with open(result, 'w') as wa:
        wa.write(header.encode('UTF-8'))
    error_file = result + '.error'
    p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'),
                         stdout=open(result, 'a'), universal_newlines=True)
    p.wait()
    returncode = p.returncode
    logger.info('%s return code is %d' % (command, returncode))


@shared_task
def xsum(numbers):
    return sum(numbers)
