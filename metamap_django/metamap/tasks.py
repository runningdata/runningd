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
from django.conf import settings
from django.utils import timezone

from metamap.helpers import etlhelper
from metamap.models import ETL, Executions, WillDependencyTask, AnaETL, Exports, SqoopHive2MysqlExecutions, \
    SqoopHive2Mysql, SqoopMysql2Hive, SqoopMysql2HiveExecutions
from will_common.utils import enums, dateutils

from celery.utils.log import get_task_logger

from will_common.utils.constants import TMP_EXPORT_FILE_LOCATION, AZKABAN_SCRIPT_LOCATION

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/metamap/'


@task
def getroot():
    return ROOT_PATH


@shared_task
def add(x, y):
    return x + y


@shared_task
def exec_sqoop(command, location):
    print('command is %s , location is %s' % (command, location))
    execution = SqoopHive2MysqlExecutions.objects.get(logLocation=location)
    execution.end_time = timezone.now()
    try:
        p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
                             shell=True,
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
def exec_sqoop2(command, location):
    print('command is %s , location is %s' % (command, location))
    execution = SqoopMysql2HiveExecutions.objects.get(logLocation=location)
    execution.end_time = timezone.now()
    try:
        p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
                             shell=True,
                             universal_newlines=True)
        p.wait()
        returncode = p.returncode
        logger.info('%s return code is %d' % (command, returncode))
        sqoop = execution.job
        if len(sqoop.partition_key) > 0 in sqoop.option:
            inmi_tbl = etlhelper.get_hive_inmi_tbl(sqoop.mysql_tbl)
            hive_cmd = 'hive -e "set hive.exec.dynamic.partition.mode=nonstrict;insert overwrite table %s partition(%s) select * from %s; drop %s;"' % \
                       (inmi_tbl, sqoop.partition_key, sqoop.mysql_tbl, inmi_tbl)
            p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
                                 shell=True,
                                 universal_newlines=True)
            p.wait()
            returncode += p.returncode
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


def exec_email_export(will_task):
    export = Exports.objects.create(task=will_task)
    try:
        ana_etl = AnaETL.objects.get(pk=will_task.rel_id)
        part = ana_etl.name + '-' + dateutils.now_datetime()
        result = TMP_EXPORT_FILE_LOCATION + part
        result_dir = result + '_dir'
        pre_insertr = "insert overwrite local directory '%s' row format delimited fields terminated by ','  " % result_dir
        sql = etlhelper.generate_sql(will_task.variables, pre_insertr + ana_etl.query)
        command = 'hive --hiveconf mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ' -e \"' + sql.replace('"',
                                                                                                              '\\"') + '\"'
        print 'command is ', command
        with open(result, 'w') as wa:
            header = ana_etl.headers
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


# TODO 处理其他类型的定时任务
def exec_hive2mysql(will_task):
    sqoop = SqoopHive2Mysql.objects.get(id=will_task.rel_id)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop-sche-' + sqoop.name + '.log'
    command = etlhelper.generate_sqoop_hive2mysql(sqoop)
    execution = SqoopHive2MysqlExecutions(logLocation=location, job_id=sqoop.id, status=0)
    execution.save()
    exec_sqoop(command, location)


def exec_etl_sche(will_task):
    etl = ETL.objects.get(id=will_task.rel_id)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sche-' + etl.tblName.replace('@', '__') + '.hql'
    etlhelper.generate_etl_file(etl, location)
    log_location = location.replace('hql', 'log')
    with open(log_location, 'a') as log:
        with open(location, 'r') as hql:
            log.write(hql.read())
    execution = Executions(logLocation=log_location, job_id=will_task.rel_id, status=0)
    execution.save()
    exec_etl('hive -f ' + location, log_location)


def exec_mysql2hive(will_task):
    sqoop = SqoopMysql2Hive.objects.get(id=will_task.rel_id)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop2-sche-' + sqoop.name + '.log'
    command = etlhelper.generate_sqoop_mysql2hive(sqoop)
    execution = SqoopMysql2HiveExecutions(logLocation=location, job_id=sqoop.id, status=0)
    execution.save()
    exec_sqoop2(command, location)


executors = {1: exec_etl_sche, 2: exec_email_export, 3: exec_hive2mysql, 4: exec_mysql2hive}


@shared_task
def exec_etl_cli(task_id):
    will_task = WillDependencyTask.objects.get(pk=task_id)
    type = will_task.type
    executors.get(type)(will_task)


@shared_task
def xsum(numbers):
    return sum(numbers)
