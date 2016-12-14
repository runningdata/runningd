# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from django.template import Context, Template

from metamap.models import TblBlood, ETL, WillDependencyTask
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

def generate_etl_sql(etl, schedule = -1):
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
        task = WillDependencyTask.objects.get(rel_id=etl.id, schedule=schedule)
        str.append(task.variables)
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


def generate_etl_file(etl, location, schedule = -1):
    '''
    生成hql文件
    :param etl:
    :param location:
    :return:
    '''
    final_result = generate_etl_sql(etl, schedule)
    with open(location, 'w') as f:
        f.write(final_result.encode('utf-8'))


def generate_job_file(blood, parent_node, folder, schedule = -1):
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
    with open(job_file,'w') as f:
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
        # if parent_node not in done_blood:

        if leaf.tblName not in done_blood:
            logger.error('not in blood : %s , doneis : %s' % (parent_node, done_blood))
            generate_job_file(leaf, parent_node, folder, schedule)
            done_blood.add(leaf.tblName)
        print('parent_node : %s ,floadr : %s , done_boloo: %s, sche: %s' %(parent_node, folder, done_blood, schedule))
        load_nodes(parent_node, folder, done_blood, schedule)
