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

from metamap.helpers import etlhelper
from metamap.models import ETL, Executions, WillDependencyTask, AnaETL, Exports
from will_common.utils import enums, dateutils

from celery.utils.log import get_task_logger

from will_common.utils.constants import TMP_EXPORT_FILE_LOCATION

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/metamap/'


@task
def getroot():
    return ROOT_PATH


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
def exec_etl_cli(task_id):
    export = Exports.objects.create(task_id=task_id)
    try:
        will_task = WillDependencyTask.objects.get(pk=task_id)
        ana_etl = AnaETL.objects.get(pk=will_task.rel_id)
        part = ana_etl.name + '-' + dateutils.now_datetime()
        sql = etlhelper.generate_sql(will_task.variables, ana_etl.query)
        result = TMP_EXPORT_FILE_LOCATION + part
        result_dir = result +'_dir'
        pre_insertr = "insert overwrite local directory '%s' row format delimited fields terminated by ','  " % result_dir
        sql = pre_insertr + sql
        command = 'hive -e \"' + sql.replace('"', '\\"') + '\"'
        print 'command is ', command
        with open(result, 'w') as wa:
            header = ana_etl.headers.replace(',', '\t')
            wa.write(header.encode('gb18030'))
            wa.write('\n')
        error_file = result + '.error'
        p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
        p.wait()
        returncode = p.returncode
        logger.info('%s return code is %d' % (command, returncode))
        command = 'cat %s/* | iconv -f utf-8 -c -t gb18030 >> %s' % (result_dir, result)
        print 'command is ', command
        p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
        p.wait()
        returncode = p.returncode
        export.end_time = timezone.now()
        export.command = command
        export.file_loc = part
        export.save()
        logger.info('%s return code is %d' % (command, returncode))
    except Exception, e:
        logger.error('ERROR: %s' % traceback.format_exc())
        export.end_time = timezone.now()
        export.file_loc = part
        export.command = traceback.format_exc()
        export.save()


@shared_task
def xsum(numbers):
    return sum(numbers)
