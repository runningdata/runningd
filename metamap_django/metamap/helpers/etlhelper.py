# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from django.template import Context, Template

from metamap.models import TblBlood, ETL
from metamap.utils import dateutils
from metamap.utils.constants import *
import logging

logger = logging.getLogger('info')

def generate_etl_sql(etl):
    '''
    预览HSQL内容
    :param etl:
    :param location:
    :return:
    '''
    str = list()
    str.append('{% load etlutils %}')
    str.append(etl.variables)
    str.append("-- job for " + etl.tblName)
    if etl.author:
        str.append("-- author : " + etl.author)
    ctime = etl.ctime
    if (ctime != None):
        str.append("-- create time : " + dateutils.format_day(ctime))
    else:
        str.append("-- cannot find ctime")
    str.append("-- pre settings ")
    str.append(etl.setting)
    str.append(etl.preSql)
    str.append(etl.query)

    template = Template('\n'.join(str));
    return template.render(Context())


def generate_etl_file(etl, location):
    '''
    生成hql文件
    :param etl:
    :param location:
    :return:
    '''
    final_result = generate_etl_sql(etl)
    with open(location, 'w') as f:
        print('hql content : %s ' % final_result)
        f.write(final_result)


def generate_job_file(blood, parent_node, folder):
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
        generate_etl_file(etl, location)
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

def load_nodes(leafs, folder, done_blood):
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
                                           + " where a.valid = 1 and a.tbl_name = '" + leaf.tblName + "'")
        if parent_node not in done_blood:
            generate_job_file(leaf, parent_node, folder)
            done_blood.add(leaf.tblName)
        load_nodes(parent_node, folder, done_blood)