# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.conf import settings
from django.template import Context, Template

from metamap.db_views import ColMeta, DB
from metamap.models import TblBlood, ETL, WillDependencyTask, SqoopMysql2Hive, SqoopHive2Mysql
from will_common.utils import dateutils
from will_common.utils.constants import *
import logging

logger = logging.getLogger('info')


def get_etl_sql(etl):
    '''
    获取替换变量后的sql内容
    :param etl:
    :return:
    '''
    str = list()
    str.append('{% load etlutils %}')
    str.append(etl.variables)
    str.append(etl.query)

    template = Template('\n'.join(str))
    return template.render(Context()).strip()


def generate_sql(variables, query):
    '''
    预览HSQL内容
    :param etl:
    :return:
    '''
    str = list()
    str.append('{% load etlutils %}')
    str.append(variables)
    str.append(query)

    template = Template('\n'.join(str))
    return template.render(Context()).strip()


def generate_sqoop_mysql2hive(task, schedule=-1):
    is_partition = True if len(task.partition_key) > 0 else False

    str = list()
    str.append('{% load etlutils %}')
    if schedule == -1:
        if task.settings and task.settings != 'None':
            str.append(task.settings)
    else:
        tt = WillDependencyTask.objects.get(rel_id=task.id, schedule=schedule, type=4)
        str.append(tt.variables)

    # sqoop --options-file/server/app/sqoop/jlc_import_hive.txt --delete-target-dir-m    23 --table    cash_record


    # --connect
    # jdbc:mysql: // 120.55 .176.18:5306/product?useCursorFetch = true & dontTrackOpenResources = true & defaultFetchSize = 2000
    # --driver
    # com.mysql.jdbc.Driver
    # --username
    # xmanread
    # --password
    # LtLUGkNbr84UWXglBFYe4GuMX8EJXeIG
    # --outdir
    # /server/app/sqoop/vo
    # --bindir
    # /server/app/sqoop/vo
    # --hive -
    # import
    # --hive-overwrite
    str.append(' sqoop import ')
    str.append('-Dmapreduce.job.queuename=' + settings.CLUTER_QUEUE)
    str.append(task.mysql_meta.settings)
    str.append(' --hive-database ')
    str.append(task.hive_meta.db)
    if task.columns:
        str.append(' --columns')
        str.append(task.columns)
    if task.where_clause:
        str.append(' --where')
        str.append(task.where_clause)
    str.append(' --table')
    if is_partition:
        str.append(get_hive_inmi_tbl(task.mysql_tbl))
    else:
        str.append(task.mysql_tbl)
    str.append(' --hive-import --hive-overwrite')
    str.append('--outdir /server/app/sqoop/vo --bindir /server/app/sqoop/vo --verbose ')
    if 'target-dir' in task.option:
        export_dir = DB.objects.using('hivemeta').filter(name=task.hive_meta.db).first().db_location_uri
        export_dir += '/'
        export_dir += task.mysql_tbl
        export_dir += '/'
        str.append(task.option.replace('target-dir', 'target-dir ' + export_dir))
    else:
        str.append(' --delete-target-dir ')
        str.append(task.option)

    template = Template(' '.join(str).replace('\n', ' ').replace('&', '\&'))
    strip = template.render(Context()).strip()
    return strip


def get_hive_inmi_tbl(tbl):
    return tbl + '_inmi'

def generate_sqoop_hive2mysql(task, schedule=-1):
    str = list()

    # sqoop --options-file/server/app/sqoop/export_hive_ykw_dw.txt --table
    # JLC_ORDER_DETAIL_APP \
    # --export-dir/apps/hive/warehouse/dim_payment.db/order_detail/log_type =${type}/log_period =${period}/log_create_date =${create_time} \
    #  --input-fields-terminated-by '\t' \
    # --update-key
    # create_date, period, type, channel_id, bank_name, platform, status_id, return_status \
    # --update-mode
    # allowinsert \
    # --columns
    # create_date, end_date, period, type, \
    # channel_id, bank_name, platform, status_id, return_status, \
    # number_order, amount_order

    # export
    # --connect
    # jdbc:mysql: // 10.0.1.73:3306/YKX_DW?useCursorFetch = true & dontTrackOpenResources = true & defaultFetchSize = 2000
    # --username
    # root
    # --password
    # data @ yinker.com
    # --connection-manager
    # org.apache.sqoop.manager.MySQLManager
    # --outdir
    # /server/app/sqoop/vo
    # --m
    # 1
    str.append('{% load etlutils %}')
    if schedule == -1:
        if task.settings and task.settings != 'None':
            str.append(task.settings)
    else:
        tt = WillDependencyTask.objects.get(rel_id=task.id, schedule=schedule, type=3)
        str.append(tt.variables)
    str.append(' sqoop export ')
    str.append('-Dmapreduce.job.queuename=' + settings.CLUTER_QUEUE)
    str.append(task.mysql_meta.settings)
    str.append(' --input-fields-terminated-by "\\t" ')
    str.append('  --update-key ')
    str.append(task.update_key)
    str.append(' --update-mode allowinsert ')
    str.append(' --columns ')
    str.append(task.columns)
    export_dir = ColMeta.objects.using('hivemeta').filter(db__name=task.hive_meta.db,
                                                          tbl__tbl_name=task.hive_tbl).first().location
    export_dir += '/'
    export_dir += task.hive_tbl
    export_dir += '/'
    if len(task.partion_expr) != 0:
        export_dir += task.partion_expr
    str.append(' --export-dir ')
    str.append(export_dir)
    str.append(' --table ')
    str.append(task.mysql_tbl)
    str.append(' --verbose ')
    str.append(task.option)

    template = Template(' '.join(str).replace('\n', ' ').replace('&', '\&'))
    strip = template.render(Context()).strip()
    return strip


def generate_etl_sql(etl, schedule=-1):
    '''
    预览HSQL内容
    :param etl:
    :return:
    '''
    str = list()
    str.append('{% load etlutils %}')
    if schedule == -1:
        str.append(etl.variables)
    else:
        task = WillDependencyTask.objects.get(rel_id=etl.id, schedule=schedule, type=1)
        str.append(task.variables)
    str.append('set mapreduce.job.queuename=' + settings.CLUTER_QUEUE +';')
    str.append("-- job for " + etl.tblName)
    if etl.author:
        str.append("-- author : " + etl.author)
    ctime = etl.ctime
    if (ctime != None):
        str.append("-- create time : " + dateutils.format_day(ctime))
    else:
        str.append("-- cannot find ctime")
    str.append("\n---------------------------------------- pre settings ")
    str.append(etl.setting)
    str.append("\n---------------------------------------- preSql ")
    str.append(etl.preSql)
    str.append("\n---------------------------------------- query ")
    str.append(etl.query)

    template = Template('\n'.join(str))
    return template.render(Context()).strip()


def generate_etl_file(etl, location, schedule=-1):
    '''
    生成hql文件
    :param etl:
    :param location:
    :return:
    '''
    final_result = generate_etl_sql(etl, schedule)
    with open(location, 'w') as f:
        f.write(final_result.encode('utf-8'))


def generate_job_file(blood, parent_node, folder, schedule=-1):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    job_name = blood.tblName
    if not job_name.startswith('etl_done_'):
        # 生成hql文件
        etl = ETL.objects.get(tblName=job_name, valid=1)
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        generate_etl_file(etl, location, schedule)
        command = "hive -f " + location
    else:
        command = "echo " + job_name

    # 生成job文件
    job_type = 'command'
    dependencies = set()
    for p in parent_node:
        dependencies.add(p.tblName)
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
    if len(dependencies) > 0:
        job_depencied = ','.join(dependencies)
        content += "dependencies=" + job_depencied + "\n"
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)


def generate_end_job_file(job_name, command, folder, deps):
    # 生成结束的job文件
    job_type = 'command'
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
    if deps:
        content += "dependencies=" + deps + "\n"
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)


def generate_job_file_h2m(objs, folder):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    for obj in objs:
        job_name = obj.name
        task = SqoopHive2Mysql.objects.get(obj.rel_id)
        command = generate_sqoop_hive2mysql(task, schedule=obj.schedule)
        # 生成job文件
        job_type = 'command'
        content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
        job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
        with open(job_file, 'w') as f:
            f.write(content)


def generate_job_file_m2h(objs, folder):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    for obj in objs:
        job_name = obj.name
        task = SqoopMysql2Hive.objects.get(pk=obj.rel_id)
        command = generate_sqoop_mysql2hive(task, schedule=obj.schedule)
        # 生成job文件
        job_type = 'command'
        content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
        job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
        with open(job_file, 'w') as f:
            f.write(content)


def load_nodes(leafs, folder, done_blood, schedule):
    '''
    遍历加载节点
    :param leafs:
    :param folder:
    :param done_blood:
    :return:
    '''
    for leaf in leafs:
        parent_node = TblBlood.objects.raw("select b.* from"
                                           + " metamap_tblblood a join metamap_tblblood b"
                                           + " on a.parent_tbl = b.tbl_name and b.valid = 1"
                                           + " JOIN metamap_willdependencytask s "
                                           + " on s.type = 1 and s.schedule = " + schedule + " and s.rel_id = b.related_etl_id"
                                           + " where a.valid = 1 and a.tbl_name = '" + leaf.tblName + "'")
        if leaf.tblName not in done_blood:
            logger.error('not in blood : %s , doneis : %s' % (parent_node, done_blood))
            generate_job_file(leaf, parent_node, folder, schedule)
            done_blood.add(leaf.tblName)
        print('parent_node : %s ,floadr : %s , done_boloo: %s, sche: %s' %(parent_node, folder, done_blood, schedule))
        load_nodes(parent_node, folder, done_blood, schedule)
