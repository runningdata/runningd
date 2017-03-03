# # !/usr/bin/env python
# # -*- coding: utf-8 -*
# import os
# import subprocess
# import traceback
#
# from django.conf import settings
# from django.utils import timezone
#
# from metamap.helpers import etlhelper
# from metamap.models import ETL, Executions, SqoopMysql2Hive, SqoopMysql2HiveExecutions, SqoopHive2Mysql, \
#     SqoopHive2MysqlExecutions, AnaETL, Exports, JarApp, JarAppExecutions, SourceApp, SourceAppExecutions
# from metamap.tasks import exec_etl, exec_m2h, exec_h2m, logger
# from will_common.models import WillDependencyTask
# from will_common.utils import dateutils
# from will_common.utils import enums
# from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION, TMP_EXPORT_FILE_LOCATION
#
#
# class CommonProcessor:
#     def __init__(self, name, p_type):
#         self.name = name
#         self.p_type = p_type
#
#     def handle_task(self, task_id):
#         pass
#
#     def type_filter(self, objs, obj):
#         return objs
#
#
# class ETLProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         etl = ETL.objects.get(id=task_id)
#         location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sche-' + etl.name.replace('@',
#                                                                                                        '__') + '.hql'
#         etlhelper.generate_etl_file(etl, location)
#         log_location = location.replace('hql', 'log')
#         with open(log_location, 'a') as log:
#             with open(location, 'r') as hql:
#                 log.write(hql.read())
#         execution = Executions(logLocation=log_location, job_id=task_id, status=0)
#         execution.save()
#         exec_etl('hive -f ' + location, log_location)
#
#     def type_filter(self, objs, obj):
#         '''
#         过滤掉无效的ETL
#         :param obj:
#         :return:
#         '''
#         etl = ETL.objects.get(id=obj.rel_id)
#         if etl.valid != 1:
#             objs = objs.exclude(id=obj.id)
#         return objs
#
#
# class M2HProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         m2h = SqoopMysql2Hive.objects.get(id=task_id)
#         location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop2-sche-' + m2h.name + '.log'
#         command = etlhelper.generate_sqoop_mysql2hive(m2h)
#         execution = SqoopMysql2HiveExecutions(logLocation=location, job_id=m2h.id, status=0)
#         execution.save()
#         exec_m2h(command, location)
#
#
# class H2MProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         h2m = SqoopHive2Mysql.objects.get(id=task_id)
#         location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-h2m-sche-' + h2m.name + '.log'
#         command = etlhelper.generate_sqoop_hive2mysql(h2m)
#         execution = SqoopHive2MysqlExecutions(logLocation=location, job_id=h2m.id, status=0)
#         execution.save()
#         exec_h2m(command, location)
#
#
# class JarAppProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         jar_task = JarApp.objects.get(pk=task_id)
#         log = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-jarapp-sche-' + jar_task.name + '.log'
#         work_dir = os.path.dirname(os.path.dirname(__file__)) + '/'
#         command = etlhelper.generate_jarapp_script(work_dir, jar_task)
#         execution = JarAppExecutions(logLocation=log, job_id=jar_task.id, status=0)
#         try:
#             p = subprocess.Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True,
#                                  universal_newlines=True)
#             p.wait()
#             returncode = p.returncode
#             logger.info('%s return code is %d' % (command, returncode))
#             if returncode == 0:
#                 execution.status = enums.EXECUTION_STATUS.DONE
#             else:
#                 execution.status = enums.EXECUTION_STATUS.FAILED
#         except Exception, e:
#             logger.error(e)
#             execution.status = enums.EXECUTION_STATUS.FAILED
#         execution.save()
#
#
# class SourceAppProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         source_task = SourceApp.objects.get(pk=task_id)
#         work_dir = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sourceapp-sche-' + source_task.name
#         os.mkdir(work_dir)
#         log = work_dir + '/exec.log'
#         command = 'sh ' + etlhelper.generate_sourceapp_script_file(work_dir, source_task)
#         execution = SourceAppExecutions(logLocation=log, job_id=source_task.id, status=0)
#         try:
#             p = subprocess.Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True,
#                                  universal_newlines=True)
#             p.wait()
#             returncode = p.returncode
#             logger.info('%s return code is %d' % (command, returncode))
#             if returncode == 0:
#                 execution.status = enums.EXECUTION_STATUS.DONE
#             else:
#                 execution.status = enums.EXECUTION_STATUS.FAILED
#         except Exception, e:
#             logger.error(e)
#             execution.status = enums.EXECUTION_STATUS.FAILED
#         execution.save()
#
#
# class ExportProcessor(CommonProcessor):
#     def handle_task(self, task_id):
#         will_task = WillDependencyTask.objects.get(rel_id=task_id, type=2)
#         export = Exports.objects.create(task=will_task)
#         try:
#             ana_etl = AnaETL.objects.get(pk=task_id)
#             part = ana_etl.name + '-' + dateutils.now_datetime()
#             result = TMP_EXPORT_FILE_LOCATION + part
#             result_dir = result + '_dir'
#             # if ana_etl.creator:
#             #     pre_insertr = "-- %s;\ninsert overwrite local directory '%s' row format delimited fields terminated by ','  " % (ana_etl.creator.user.username + '-' + ana_etl.name, result_dir)
#             # else:
#             pre_insertr = "insert overwrite local directory '%s' row format delimited fields terminated by ','  " % result_dir
#             sql = etlhelper.generate_sql(will_task.variables, pre_insertr + ana_etl.query)
#             command = 'hive --hiveconf mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ' -e \"' + sql.replace('"',
#                                                                                                                   '\\"') + '\"'
#             print 'command is ', command
#             with open(result, 'w') as wa:
#                 header = ana_etl.headers
#                 wa.write(header.encode('gb18030'))
#                 wa.write('\n')
#             error_file = result + '.error'
#             p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
#             p.wait()
#             returncode = p.returncode
#             logger.info('%s return code is %d' % (command, returncode))
#             export.command = command
#             command = 'cat %s/* | iconv -f utf-8 -c -t gb18030 >> %s' % (result_dir, result)
#             print 'command is ', command
#             p = subprocess.Popen([''.join(command)], shell=True, stderr=open(error_file, 'a'), universal_newlines=True)
#             p.wait()
#             returncode = p.returncode
#             export.end_time = timezone.now()
#             export.file_loc = part
#             export.save()
#             logger.info('%s return code is %d' % (command, returncode))
#         except Exception, e:
#             logger.error('ERROR: %s' % traceback.format_exc())
#             export.end_time = timezone.now()
#             export.file_loc = part
#             export.command = traceback.format_exc()
#             export.save()
#
#     def type_filter(self, objs, obj):
#         objs = objs.exclude(id=obj.id)
#         return objs
#
#
# processors = (
#     CommonProcessor('None', 0),
#     ETLProcessor('H2H', 1), ExportProcessor('Export', 2), H2MProcessor('H2M', 3), M2HProcessor('M2H', 4),
#     SourceAppProcessor('SourceApp', 5), JarAppProcessor('JarApp', 6)
# )
