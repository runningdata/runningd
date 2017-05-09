# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import traceback

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from rest_framework import viewsets

from metamap.helpers import etlhelper
from metamap.models import SqoopMysql2Hive, Meta, SqoopMysql2HiveExecutions
from will_common.models import WillDependencyTask
from will_common.utils import PushUtils
from will_common.utils import dateutils
from will_common.utils import encryptutils
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils import ziputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION, AZKABAN_BASE_LOCATION
from will_common.views.common import GroupListView

logger = logging.getLogger('info')


class Mysql2HiveListView(GroupListView):
    template_name = 'sqoop/list2.html'
    context_object_name = 'objs'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            search = self.request.GET['search']
            return SqoopMysql2Hive.objects.filter(name__contains=search).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return SqoopMysql2Hive.objects.all().order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(Mysql2HiveListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def add(request):
    if request.method == 'POST':
        sqoop = SqoopMysql2Hive()
        httputils.post2obj(sqoop, request.POST, 'id')
        userutils.add_current_creator(sqoop, request)
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/m2h/')
    else:
        return render(request, 'sqoop/edit2.html')


def edit(request, pk):
    if request.method == 'POST':
        sqoop = SqoopMysql2Hive.objects.get(pk=int(pk))
        httputils.post2obj(sqoop, request.POST, 'id')
        userutils.add_current_creator(sqoop, request)
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/m2h/')
    else:
        obj = SqoopMysql2Hive.objects.get(pk=pk)
        return render(request, 'sqoop/edit2.html', {'obj': obj})


def exec_job(request, sqoopid):
    sqoop = SqoopMysql2Hive.objects.get(id=sqoopid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop-' + sqoop.name + '.log'
    command = etlhelper.generate_sqoop_mysql2hive(sqoop)
    execution = SqoopMysql2HiveExecutions(logLocation=location, job_id=sqoopid, status=0)
    execution.save()
    from metamap import tasks
    tasks.exec_m2h.delay(command, location)
    return redirect('metamap:sqoop2_execlog', execid=execution.id)


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'sqoop/exec_log2.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = SqoopMysql2HiveExecutions.objects.get(pk=execid)

    try:
        with open(execution.logLocation, 'r') as log:
            content = log.read().replace('\n', '<br>')
    except:
        return HttpResponse('')
    return HttpResponse(content)


def review(request, sqoop_id):
    try:
        sqoop = SqoopMysql2Hive.objects.get(id=sqoop_id)
        hql = etlhelper.generate_sqoop_mysql2hive(sqoop)
        # return render(request, 'etl/review_sql.html', {'obj': etl, 'hql': hql})
        return HttpResponse(hql.replace('--', '<br>--'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def generate_job_dag(request, schedule, group_name='xiaov'):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        folder = 'm2h-' + dateutils.now_datetime()
        leafs = WillDependencyTask.objects.filter(schedule=schedule, type=4, valid=1)
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.generate_job_file_m2h(leafs, folder, group_name)

        job_name = 'm2h_done_' + group_name + '_' + dateutils.now_datetime()
        command = 'echo done for sqoop'
        deps = set()
        for leaf in leafs:
            if SqoopMysql2Hive.objects.get(pk=leaf.rel_id).cgroup.name == group_name:
                deps.add(leaf.name)
        etlhelper.generate_end_job_file(job_name, command, folder, ','.join(deps))
        PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE), '%d m2h generated ' % len(leafs))
        PushUtils.push_exact_email(settings.ADMIN_EMAIL, '%d m2h generated ' % len(deps))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')
