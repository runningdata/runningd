# -*- coding: utf-8 -*
from django.template import Context
from django.template import Template


def get_etl_sql(etl):
    '''
    获取替换变量后的sql内容
    :param etl:
    :return:
    '''
    str = list()
    str.append('{% load etlutils %}')
    str.append(etl.setting)
    str.append(etl.variables)
    str.append(etl.query)

    template = Template('\n'.join(str))
    return template.render(Context()).strip()