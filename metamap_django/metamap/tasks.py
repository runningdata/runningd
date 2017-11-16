# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import os
import subprocess

from billiard import SoftTimeLimitExceeded
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from metamap.helpers import etlhelper
from metamap.models import WillDependencyTask, ExecObj, ExecutionsV2, WillTaskV2, ExecBlood, ETL, TblBlood
from will_common.utils import PushUtils
from will_common.utils import encryptutils
from will_common.utils import enums, dateutils

from celery.utils.log import get_task_logger

from will_common.utils import ziputils
from azkaban_client.azkaban import *
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION, AZKABAN_BASE_LOCATION

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/metamap/'


# @shared_task
# def exec_h2m(command, location, name=''):
#     print('command is %s , location is %s' % (command, location))
#     execution = SqoopHive2MysqlExecutions.objects.get(logLocation=location)
#     execution.end_time = timezone.now()
#     try:
#         p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
#                              shell=True,
#                              universal_newlines=True)
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         if returncode == 0:
#             execution.status = enums.EXECUTION_STATUS.DONE
#         else:
#             execution.status = enums.EXECUTION_STATUS.FAILED
#     except Exception, e:
#         logger.error(e)
#         execution.status = enums.EXECUTION_STATUS.FAILED
#     execution.end_time = timezone.now()
#     execution.save()


# @shared_task
# def exec_m2h(command, location, name=''):
#     print('command is %s , location is %s' % (command, location))
#     execution = SqoopMysql2HiveExecutions.objects.get(logLocation=location)
#     execution.end_time = timezone.now()
#     try:
#         p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
#                              shell=True,
#                              universal_newlines=True)
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         sqoop = execution.job
#         if len(sqoop.partition_key) > 0 in sqoop.option:
#             inmi_tbl = etlhelper.get_hive_inmi_tbl(sqoop.mysql_tbl)
#             hive_cmd = 'hive -e "use %s;set hive.exec.dynamic.partition.mode=nonstrict;insert overwrite table %s partition(%s) select * from %s; drop table %s;"' % \
#                        (sqoop.hive_meta.meta, sqoop.mysql_tbl, sqoop.partition_key, inmi_tbl, inmi_tbl)
#             # p = subprocess.Popen([''.join(hive_cmd)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
#             #                      shell=True,
#             #                      universal_newlines=True)
#             # p.wait()
#             # returncode += p.returncode
#             logger.info('%s hive_cmd return code is %d' % (hive_cmd, returncode))
#         if returncode == 0:
#             execution.status = enums.EXECUTION_STATUS.DONE
#         else:
#             execution.status = enums.EXECUTION_STATUS.FAILED
#     except Exception, e:
#         logger.error('ERROR: %s' % traceback.format_exc())
#         logger.error(e)
#         execution.status = enums.EXECUTION_STATUS.FAILED
#     execution.end_time = timezone.now()
#     execution.save()
#
#
# @shared_task
# def exec_etl(command, log, name=''):
#     execution = Executions.objects.get(logLocation=log)
#     execution.end_time = timezone.now()
#     try:
#         p = subprocess.Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True,
#                              universal_newlines=True)
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         if returncode == 0:
#             execution.status = enums.EXECUTION_STATUS.DONE
#         else:
#             execution.status = enums.EXECUTION_STATUS.FAILED
#     except Exception, e:
#         logger.error(e)
#         execution.status = enums.EXECUTION_STATUS.FAILED
#     execution.end_time = timezone.now()
#     execution.save()
#
#
# def exec_email_export(taskid):
#     will_task = WillDependencyTask.objects.get(rel_id=taskid, type=2)
#     export = Exports.objects.create(task=will_task)
#     try:
#         ana_etl = AnaETL.objects.get(pk=taskid)
#         if ana_etl.name.startswith('common_'):
#             part = ana_etl.name + '-' + dateutils.now_datekey()
#         else:
#             part = ana_etl.name + '-' + dateutils.now_datetime()
#         result = TMP_EXPORT_FILE_LOCATION + part
#         result_dir = result + '_dir'
#         # if ana_etl.creator:
#         #     pre_insertr = "-- %s;\ninsert overwrite local directory '%s' row format delimited fields terminated by ','  " % (ana_etl.creator.user.username + '-' + ana_etl.name, result_dir)
#         # else:
#         pre_insertr = "insert overwrite local directory '%s' row format delimited fields terminated by ','  " % result_dir
#         sql = etlhelper.generate_sql(will_task.variables, pre_insertr + ana_etl.query)
#         command = 'hive --hiveconf mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ' -e \"' + sql.replace('"',
#                                                                                                               '\\"') + '\"'
#         print 'command is ', command
#         with open(result, 'w') as wa:
#             header = ana_etl.headers
#             wa.write(header.encode('gb18030'))
#             wa.write('\n')
#         error_file = result + '.error'
#         p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         export.command = command
#         command = 'cat %s/* | iconv -f utf-8 -c -t gb18030 >> %s' % (result_dir, result)
#         print 'command is ', command
#         p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
#         p.wait()
#         returncode = p.returncode
#         export.end_time = timezone.now()
#         export.file_loc = part
#         export.save()
#         shutil.rmtree(result_dir)
#         logger.info('%s return code is %d' % (command, returncode))
#     except Exception, e:
#         logger.error('ERROR: %s' % traceback.format_exc())
#         export.end_time = timezone.now()
#         export.file_loc = part
#         export.command = traceback.format_exc()
#         export.save()
#
#
# # TODO 处理其他类型的定时任务
# def exec_hive2mysql(taskid):
#     h2m = SqoopHive2Mysql.objects.get(id=taskid)
#     location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-h2m-sche-' + h2m.name + '.log'
#     command = etlhelper.generate_sqoop_hive2mysql(h2m)
#     execution = SqoopHive2MysqlExecutions(logLocation=location, job_id=h2m.id, status=0)
#     execution.save()
#     exec_h2m(command, location)
#
#
# def exec_etl_sche(taskid):
#     etl = ETL.objects.get(id=taskid)
#     location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sche-' + etl.name.replace('@', '__') + '.hql'
#     etlhelper.generate_etl_file(etl, location)
#     log_location = location.replace('hql', 'log')
#     with open(log_location, 'a') as log:
#         with open(location, 'r') as hql:
#             log.write(hql.read())
#     execution = Executions(logLocation=log_location, job_id=taskid, status=0)
#     execution.save()
#     exec_etl('hive -f ' + location, log_location)
#
#
# def exec_mysql2hive(taskid):
#     m2h = SqoopMysql2Hive.objects.get(id=taskid)
#     location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop2-sche-' + m2h.name + '.log'
#     command = etlhelper.generate_sqoop_mysql2hive(m2h)
#     execution = SqoopMysql2HiveExecutions(logLocation=location, job_id=m2h.id, status=0)
#     execution.save()
#     exec_m2h(command, location)


@shared_task
def tail_hdfs(logLocation, command, name=''):
    print 'command is ', command
    with open(logLocation, 'a') as fi:
        p = subprocess.Popen([''.join(command)], stdout=fi, stderr=subprocess.STDOUT,
                             shell=True,
                             universal_newlines=True)
        p.wait()
        returncode = p.returncode
    os.rename(logLocation, logLocation + '_done')
    # PushUtils.push_exact_email(email, msg)
    logger.info('tail_hdfs : %s return code is %d' % (command, returncode))


# @shared_task
# def exec_sourceapp(taskid, name=''):
#     '''
#     1. cd wd
#     2. git clone
#     3. compile_tool
#     4. run main func
#
#     wd = mkdir(randomkey)
#
#     shell:
#         cd ${wd}
#         git clone ${git_url}
#         cd ${sub_dir}
#         ${compile_tool}  ${compile_opts}
#         cd ${target}  // target
#         ${engine_cmd} -cp *.jar ${run_opts} ${main_func}
#
#     :param will_task:
#     :return:
#     '''
#     source_task = SourceApp.objects.get(pk=taskid)
#     work_dir = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sourceapp-sche-' + source_task.name
#     os.mkdir(work_dir)
#     log = work_dir + '/exec.log'
#     command = 'sh ' + etlhelper.generate_sourceapp_script_file(work_dir, source_task)
#     execution = SourceAppExecutions(logLocation=log, job_id=source_task.id, status=0)
#     normal_execution(command, execution)
#
#
# def exec_jarapp(taskid):
#     jar_task = JarApp.objects.get(pk=taskid)
#     log = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-jarapp-sche-' + jar_task.name + '.log'
#     work_dir = os.path.dirname(os.path.dirname(__file__)) + '/'
#     command = etlhelper.generate_jarapp_script(work_dir, jar_task)
#     print command
#     execution = JarAppExecutions(logLocation=log, job_id=jar_task.id, status=0, owner=jar_task.creator)
#     command = 'runuser -l ' + jar_task.cgroup.name + ' -c "' + command + '"'
#     normal_execution(command, execution)
#
#
# @shared_task
# def exec_jar(command, pk, name=''):
#     try:
#         execution = JarAppExecutions.objects.get(pk=pk)
#         groupuser = JarApp.objects.get(pk=execution.job_id).cgroup.name
#         command = 'runuser -l ' + groupuser + ' -c "' + command + '"'
#         p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
#                              shell=True,
#                              universal_newlines=True)
#         execution.pid = p.pid
#         execution.save()
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         if returncode == 0:
#             execution.status = enums.EXECUTION_STATUS.DONE
#         else:
#             execution.status = enums.EXECUTION_STATUS.FAILED
#     except Exception, e:
#         logger.error(e)
#         execution.status = enums.EXECUTION_STATUS.FAILED
#     execution.end_time = timezone.now()
#     execution.save()
#
#
# def normal_execution(command, execution):
#     try:
#         p = subprocess.Popen([''.join(command)], stdout=open(execution.logLocation, 'a'), stderr=subprocess.STDOUT,
#                              shell=True,
#                              universal_newlines=True)
#         execution.pid = p.pid
#         execution.save()
#         p.wait()
#         returncode = p.returncode
#         logger.info('%s return code is %d' % (command, returncode))
#         if returncode == 0:
#             execution.status = enums.EXECUTION_STATUS.DONE
#         else:
#             execution.status = enums.EXECUTION_STATUS.FAILED
#     except Exception, e:
#         logger.error(e)
#         execution.status = enums.EXECUTION_STATUS.FAILED
#     execution.end_time = timezone.now()
#     execution.save()
#
#
# executors = {1: exec_etl_sche, 2: exec_email_export, 3: exec_hive2mysql, 4: exec_mysql2hive, 5: exec_sourceapp,
#              6: exec_jarapp}
#
#
# @shared_task
# def exec_etl_cli(task_id, name=''):
#     will_task = WillDependencyTask.objects.get(pk=task_id)
#     executors.get(will_task.type)(will_task.rel_id)


@shared_task
def exec_execobj(exec_id, schedule=-1, name=''):
    try:
        obj = ExecObj.objects.get(pk=exec_id)
        tt = dateutils.now_datetime()
        log_location = AZKABAN_SCRIPT_LOCATION + obj.name.replace('@', '__') + '-' + tt + '.error'
        script_location = AZKABAN_SCRIPT_LOCATION + obj.name.replace('@', '__') + '-' + tt + '.rd'
        execution = ExecutionsV2.objects.create(job=obj, log_location=log_location,
                                                cmd_shot=obj.get_cmd(schedule=schedule, location=script_location))
        execution.end_time = timezone.now()
        command = execution.cmd_shot
        try:
            p = subprocess.Popen([''.join(command)], stdout=open(log_location, 'a'), stderr=subprocess.STDOUT,
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
        execution.end_time = timezone.now()
        execution.save()
    except SoftTimeLimitExceeded, e:
        logger.error(e)
        execution.status = enums.EXECUTION_STATUS.FAILED
        execution.end_time = timezone.now()
        execution.save()


@shared_task
def exec_will(task_id, **kwargs):
    willtask = WillTaskV2.objects.get(pk=task_id)
    if willtask.valid == 0:
        print('{task} is invalid, so passed'.format(task=willtask.name))
        return
    tasks = willtask.tasks.all()
    if len(tasks) > 1:
        # batch, generate execution plan or generate azkaban job files
        # maybe the dependency relations are not as same as its blood dag, for a->b->c, maybe we just want b->c,
        # excluding a. Then a temporary dependency dag for just the few execobjs should be supplied by user.
        # The easiest way is an ordered list, but the task executions will be sequential. We could make the
        # executions parallel.
        # jobs run parallel
        folder = 'schedule_flow_' + willtask.name + '_' + dateutils.now_datetime()
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        task_ids = [execobj.id for execobj in tasks]
        for execobj in tasks:
            bloods = ExecBlood.objects.filter(child_id=execobj, parent_id__in=task_ids)
            parent_names = [etlhelper.get_name(blood.parent) for blood in bloods]
            etlhelper.generate_job_file_v2(execobj, parent_names, folder)

        PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE),
                                   '%s generated for group %s ' % (len(tasks), folder))
        PushUtils.push_exact_email(settings.ADMIN_EMAIL, '%s generated for group %s ' % (len(tasks), folder))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        print('user: %s password: %s' % (os.getenv('AZKABAN_USER'), os.getenv('AZKABAN_PWD')))
        fetcher = CookiesFetcher(os.getenv('AZKABAN_USER'), os.getenv('AZKABAN_PWD'))
        project = Project(folder, 'first test', fetcher)
        project.create_prj()
        project.upload_zip(AZKABAN_BASE_LOCATION + folder + '.zip')
        for flow in project.fetch_flow():
            execution = flow.execute()
            print('%s %s has been started ....' % (execution.prj_name, flow.flowId))
    else:
        # single
        exec_execobj(willtask.tasks[0].id, schedule=4, name=kwargs['name'])


@shared_task
def exec_etl_cli2(task_id, name=''):
    exec_task = WillDependencyTask.objects.get(pk=task_id, type=100)
    exec_execobj(exec_task.rel_id, schedule=4, name=name)

    # obj = ExecObj.objects.get(pk=exec_task.rel_id)
    # executors.get(obj.type)(obj.rel_id)


@shared_task
def xsum(numbers, name=''):
    return sum(numbers)
