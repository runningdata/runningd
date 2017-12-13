# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import os

import re
from django.conf import settings
from django.template import Context, Template

from metamap.db_views import ColMeta, DB
from metamap.models import TblBlood, ETL, WillDependencyTask, SqoopMysql2Hive, SqoopHive2Mysql, ExecBlood, ExecObj
from will_common.templatetags import etlutils
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import *
import logging

from will_common.utils.customexceptions import RDException

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
        str.append(task.mysql_tbl)
        str.append(' --hive-table ' + get_hive_inmi_tbl(task.mysql_tbl))
    else:
        str.append(task.mysql_tbl)
    str.append(' --hive-import --hive-overwrite')
    str.append(' --target-dir ')
    str.append(task.hive_meta.meta + '_' + task.name)
    str.append('--outdir /server/app/sqoop/vo --bindir /server/app/sqoop/vo --verbose ')
    str.append(' -m %d ' % task.parallel)
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


def generate_jarapp_script(wd, task, schedule=-1):
    '''
    1. mvn build
    2. app run
    :param task:
    :param schedule:
    :return:
    '''
    str = list()
    context = Context()
    context['task'] = task
    context['wd'] = wd
    if task.engine_type.id == 1:
        with open('metamap/config/spark_template.sh') as tem:
            str.append(tem.read())
    elif task.engine_type.id == 2:
        with open('metamap/config/hadoop_template.sh') as tem:
            str.append(tem.read())
    elif task.engine_type.id == 4:
        # 看看zip是否已经解压，先解压到指定目录
        zipfile = wd + task.jar_file.name
        dir = wd + 'jars/' + task.name + '/'
        if not os.path.exists(dir):
            ziputils.unzip(zipfile, dir)
        deps = [f for f in os.listdir(dir) if f.endswith('.zip') or f.endswith('.egg') or f.endswith('.py')]
        if len(deps) > 0:
            context['deps'] = ','.join(deps)
        context['wd'] = dir
        with open('metamap/config/pyspark_template.sh') as tem:
            str.append(tem.read())
    else:
        with open('metamap/config/jar_template.sh') as tem:
            str.append(tem.read())
    template = Template('\n'.join(str))
    strip = template.render(context).strip()
    strip = '{% load etlutils %} \n' + strip
    template = Template(strip)
    strip2 = template.render(Context()).strip()
    return strip2


def generate_sourceapp_script(wd, task, schedule=-1):
    '''
    1. mvn build
    2. app run
    :param task:
    :param schedule:
    :return:
    '''
    str = list()
    context = Context()
    context['wd'] = wd
    context['sourceapp'] = task
    with open('metamap/config/template.sh') as tem:
        str.append(tem.read())
    template = Template('\n'.join(str))
    strip = template.render(context).strip()
    return strip


def generate_sourceapp_script_file(wd, task, schedule=-1):
    '''
    1. mvn build
    2. app run
    :param wd:
    :param task:
    :param schedule:
    :return:
    '''
    content = generate_sourceapp_script(wd, task, schedule)
    filename = wd + '/exec.sh'
    with open(filename, 'w') as fi:
        fi.write(content.encode('utf-8'))
    return filename


def get_hive_inmi_tbl(tbl):
    return tbl + '_inmi'


def generate_sqoop_hive2mysql(task, schedule=-1, delta=0):
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
        if delta != 0:
            str.append(get_delta_variables(tt.variables, delta))
        else:
            str.append(tt.variables)
    str.append(' sqoop export ')
    str.append('-Dmapreduce.job.queuename=' + settings.CLUTER_QUEUE)
    str.append(task.mysql_meta.settings)
    if 'input-fields-terminated-by' not in task.option:
        str.append(' --input-fields-terminated-by "\\t" ')
    str.append('  --update-key ')
    str.append(task.update_key)
    str.append(' --update-mode allowinsert ')
    str.append(' --columns ')
    str.append(task.columns)
    if not settings.DEBUG:
        export_dir = ColMeta.objects.using('hivemeta').filter(db__name=task.hive_meta.db,
                                                              tbl__tbl_name=task.hive_tbl).first().location
    else:
        export_dir = ''
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
    str.append(' -m %d ' % task.parallel)
    str.append(task.option)

    template = Template(' '.join(str).replace('\n', ' ').replace('&', '\&'))
    strip = template.render(Context()).strip()
    return strip


def get_delta_variables(variables, delta):
    lines = variables.split('\n')
    new_lines = set()
    for line in lines:
        result = re.split(r'\s+', line)
        for i in result:
            if re.match(r'^[a-zA-Z_]{1,}$', i):
                if hasattr(etlutils, i):
                    method = getattr(etlutils, i)
                    if getattr(method, 'func_name') == 'day_change':
                        try:
                            num = int(result[result.index(i) + 1]) - delta
                        except Exception, e:
                            print result[result.index(i) + 1]
                            print result
                            raise e
                        result[result.index(i) + 1] = str(num)
        new_lines.add(' '.join(result))
    return '\n'.join(new_lines)


def generate_etl_sql(etl, schedule=-1, delta=0):
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
        if delta != 0:
            str.append(get_delta_variables(task.variables, delta))
        else:
            str.append(task.variables)
    str.append('set mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ';')
    str.append("-- job for " + etl.name)
    if etl.creator:
        str.append("-- " + etl.creator.user.username + '-' + etl.name)
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


def generate_etl_file(etl, location, schedule=-1, delta=0):
    '''
    生成hql文件
    :param etl:
    :param location:
    :return:
    '''
    final_result = generate_etl_sql(etl, schedule, delta)
    if final_result != MSG_NO_DATA:
        with open(location, 'w') as f:
            f.write(final_result.encode('utf-8'))


def generate_job_file(*args, **kwargs):
    # def generate_job_file(blood, parent_node, folder, schedule=-1):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    blood = kwargs['blood']
    parent_node = kwargs['parent_node']
    folder = kwargs['folder']
    schedule = kwargs.get('schedule', -1)
    is_check = kwargs.get('is_check', False)

    job_name = blood.tblName
    if not job_name.startswith('etl_done_') and not is_check:
        # 生成hql文件
        etl = ETL.objects.get(id=blood.relatedEtlId, valid=1)
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        generate_etl_file(etl, location, schedule)
        command = "hive -f " + location
        if not settings.USE_ROOT:
            command = 'runuser -l ' + etl.cgroup.name + ' -c "' + command + '"'
            # command = 'runuser -l ' + settings.PROC_USER + ' -c "' + command + '"'
    else:
        command = "echo " + job_name

    # 生成job文件
    job_type = ' command\nretries=3\nretry.backoff=60000\n'
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


def generate_job_file_v2(etlobj, parent_names, folder, schedule=-1):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_names:
    :param folder:
    :return:
    '''
    job_name = get_name(etlobj)
    if not job_name.startswith('etl_v2_done_'):
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        cmd = etlobj.get_cmd(schedule, location)
    else:
        cmd = "echo " + job_name
    # 生成job文件
    job_type = ' command\nretries=5\nretry.backoff=60000\n'
    dependencies = set()
    for p in parent_names:
        dependencies.add(p)
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + cmd + '\n'
    if len(dependencies) > 0:
        job_depencied = ','.join(dependencies)
        content += "dependencies=" + job_depencied + "\n"
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)


def generate_job_file_for_partition(job_name, parent_names, folder, schedule=-1, delta=0):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_names:
    :param folder:
    :return:
    '''
    if not job_name.startswith('etl_done_'):
        # 生成hql文件
        etl = ETL.objects.get(name=job_name, valid=1)
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        generate_etl_file(etl, location, schedule, delta)
        command = "hive -f " + location
        # command = 'runuser -l ' + settings.PROC_USER + ' -c "' + command + '"'
    else:
        command = "echo " + job_name

    # 生成job文件
    job_type = ' command\nretries=5\nretry.backoff=60000\n'
    dependencies = set()
    for p in parent_names:
        dependencies.add(p)
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


def generate_job_file_h2m(objs, folder, group_name, delta=0):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    for obj in objs:
        job_name = obj.name
        task = SqoopHive2Mysql.objects.get(pk=obj.rel_id)
        if task.cgroup.name == group_name:
            generate_h2m_script(folder, job_name, obj.schedule, task, delta)


def generate_job_file_h2m_restart(objs, folder, schedule, delta=0):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    for obj in objs:
        job_name = obj.name
        task = SqoopHive2Mysql.objects.get(pk=obj.rel_id)
        generate_h2m_script(folder, job_name, schedule, task, delta)


def generate_h2m_script(folder, job_name, schedule, task, delta=0):
    h2m = generate_sqoop_hive2mysql(task, schedule, delta)
    sqoop_file = AZKABAN_SCRIPT_LOCATION + folder + "/" + job_name + ".h2m"
    with open(sqoop_file, 'w') as f:
        f.write(h2m)
    command = 'sh ' + sqoop_file
    if not settings.USE_ROOT:
        command = 'runuser -l ' + task.cgroup.name + ' -c "' + command + '"'
    # 生成job文件
    # job_type = 'command\nretries=12\nretry.backoff=300000\n'
    job_type = ' command\nretries=5\nretry.backoff=300000\n'
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command =  ' + command + '\n'
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)


def generate_job_file_m2h(objs, folder, group_name):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_node:
    :param folder:
    :return:
    '''
    for obj in objs:
        task = SqoopMysql2Hive.objects.get(pk=obj.rel_id)
        job_name = task.name
        if task.cgroup.name == group_name:
            generate_m2h_script(folder, job_name, obj.schedule, task)


def generate_m2h_script(folder, job_name, schedule, task):
    m2h = generate_sqoop_mysql2hive(task, schedule=schedule)
    sqoop_file = AZKABAN_SCRIPT_LOCATION + folder + "/" + job_name + ".m2h"
    with open(sqoop_file, 'w') as f:
        f.write(m2h)
    command = 'sh ' + sqoop_file
    if not settings.USE_ROOT:
        command = 'runuser -l ' + task.cgroup.name + ' -c "' + command + '"'
    # 生成job文件
    # job_type = ' command \nretries=12\nretry.backoff=300000\n'
    job_type = ' command\nretries=12\nretry.backoff=300000\n'
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)


def load_nodes(*args, **kwargs):
    # def load_nodes(leafs, folder, done_blood, done_leaf, schedule, group_name):
    leafs = kwargs.get('leafs')
    folder = kwargs.get('folder')
    done_blood = kwargs.get('done_blood')
    done_leaf = kwargs.get('done_leaf')
    schedule = kwargs.get('schedule', -1)
    group_name = kwargs.get('group_name', 'jlc')
    is_check = kwargs.get('is_check', False)
    '''
    遍历加载节点
    :param leafs:
    :param folder:
    :param done_blood:
    :return:
    '''
    for leaf in leafs:
        tbl_name = leaf.tblName
        if ETL.objects.filter(name=tbl_name, cgroup__name=group_name, valid=1).count() == 1:
            if tbl_name not in done_leaf:
                print('handling... %s ' % tbl_name)
                parent_node = TblBlood.objects.raw("select b.* from"
                                                   + " metamap_tblblood a join metamap_tblblood b"
                                                   + " on a.parent_tbl = b.tbl_name and b.valid = 1"
                                                   + " JOIN metamap_willdependencytask s "
                                                   + " on s.type = 1 and s.schedule = " + schedule + " and s.rel_id = b.related_etl_id"
                                                   + " where a.valid = 1 and a.tbl_name = '" + leaf.tblName + "'")
                if tbl_name not in done_blood:
                    print('not in blood : %s ' % tbl_name)
                    generate_job_file(blood=leaf, parent_node=parent_node, folder=folder, schedule=schedule,
                                      is_check=is_check)
                    done_blood.add(tbl_name)
                print('parent_node for : %s ,floadr : %s ,sche: %s' % (tbl_name, folder, schedule))
                done_leaf.add(tbl_name)
                # load_nodes(parent_node, folder, done_blood, done_leaf, schedule, group_name)
                load_nodes(leafs=parent_node, folder=folder, done_blood=done_blood, done_leaf=done_leaf,
                           schedule=schedule, group_name=group_name, is_check=is_check)


def load_nodes_v2(leafs, folder, done_blood, done_leaf, schedule):
    '''
    遍历加载节点
    :param leafs:
    :param folder:
    :param done_blood:
    :return:
    '''
    for leaf in leafs:
        if leaf not in done_leaf:
            bloods = ExecBlood.objects.filter(child_id=leaf)
            print('handling leaf : %s ' % leaf)
            leaf_dependencies = set()
            parent_ids = set()
            for blood in bloods:
                parent = ExecObj.objects.get(pk=blood.parent.id)
                tasks = WillDependencyTask.objects.filter(schedule=schedule, rel_id=parent.id, valid=1, type=100)
                if tasks.count() == 1:
                    parent_ids.add(parent.id)
                    leaf_dependencies.add(get_name(parent))

            # 这里只会给给child生成job文件，而不会给他的parent生成 —— 新版本中应该生成！！！
            # 或者： 外面单独为最顶层的parent任务生成job列表
            child = ExecObj.objects.get(pk=leaf)
            generate_job_file_v2(child, leaf_dependencies, folder,
                                 schedule=schedule)
            done_leaf.add(leaf)
            load_nodes_v2(parent_ids, folder, done_blood, done_leaf, schedule)


def get_name(etlobj):
    '''
    m2h 和 h2m的名字不能直接取parent的name，需要拼meta和tblname
    :param etlobj:
    :return:
    '''
    if etlobj.type == 1:
        print('parent is ETL %s ' % etlobj.name)
        return etlobj.name
    elif etlobj.type == 3:
        print('parent is SqoopHive2Mysql %s ' % etlobj.name)
        etlobj = SqoopHive2Mysql.objects.get(pk=etlobj.rel_id)
        tbl_name = etlobj.hive_meta.meta + '@' + etlobj.hive_tbl
        return 'export_' + tbl_name
    elif etlobj.type == 4:
        print('parent is SqoopMysql2Hive %s ' % etlobj.name)
        etlobj = SqoopMysql2Hive.objects.get(pk=etlobj.rel_id)
        tbl_name = etlobj.hive_meta.meta + '@' + etlobj.mysql_tbl
        return 'import_' + tbl_name
    else:
        raise RDException('cannot find parent name for parent %s' % etlobj.name)
