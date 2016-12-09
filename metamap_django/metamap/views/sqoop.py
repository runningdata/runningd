# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import generic
from rest_framework import viewsets

from metamap.helpers import etlhelper
from metamap.models import SqoopHive2Mysql, Meta, SqoopHive2MysqlExecutions
from metamap.serializers import MetaSerializer
from will_common.utils import dateutils
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION

logger = logging.getLogger('info')


class SqoopHiveMetaViewSet(viewsets.ModelViewSet):
    queryset = Meta.objects.filter(type=2).order_by('-ctime')
    serializer_class = MetaSerializer

class SqoopMysqlMetaViewSet(viewsets.ModelViewSet):
    queryset = Meta.objects.filter(type=1).order_by('-ctime')
    serializer_class = MetaSerializer

class Hive2MysqlListView(generic.ListView):
    template_name = 'sqoop/list.html'
    context_object_name = 'objs'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            search = self.request.GET['search']
            return SqoopHive2Mysql.objects.filter(sqoop__contains=search).order_by('ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return SqoopHive2Mysql.objects.all()

    def get_context_data(self, **kwargs):
        context = super(Hive2MysqlListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context

def add(request):
    if request.method == 'POST':
        sqoop = SqoopHive2Mysql()
        httputils.post2obj(sqoop, request.POST, 'id')
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/sqoop/')
    else:
        return render(request, 'sqoop/edit.html')

def edit(request, pk):
    if request.method == 'POST':
        sqoop = SqoopHive2Mysql.objects.get(pk=int(pk))
        httputils.post2obj(sqoop, request.POST, 'id')
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/sqoop/')
    else:
        obj = SqoopHive2Mysql.objects.get(pk=pk)
        return render(request, 'sqoop/edit.html', {'obj': obj})

def exec_job(request, sqoopid):
    sqoop = SqoopHive2Mysql.objects.get(id=sqoopid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sqoop-' + sqoop.name + '.log'
    command = etlhelper.generate_sqoop_hive2mysql(sqoop)
    execution = SqoopHive2MysqlExecutions(logLocation=location, job_id=sqoopid, status=0)
    execution.save()
    from metamap import tasks
    tasks.exec_sqoop.delay(command, location)
    return redirect('metamap:sqoop_execlog', execid=execution.id)

def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'sqoop/exec_log.html', {'execid': execid})

def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = SqoopHive2MysqlExecutions.objects.get(pk=execid)

    try:
        with open(execution.logLocation, 'r') as log:
            content = log.read().replace('\n', '<br>')
    except:
        return HttpResponse('')
    return HttpResponse(content)

def review(request, sqoop_id):
    try:
        sqoop = SqoopHive2Mysql.objects.get(id=sqoop_id)
        hql = etlhelper.generate_sqoop_hive2mysql(sqoop)
        # return render(request, 'etl/review_sql.html', {'obj': etl, 'hql': hql})
        return HttpResponse(hql.replace('--', '<br>--'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)

class StatusJobView(generic.ListView):
    template_name = 'sqoop/executions_status.html'
    context_object_name = 'executions'
    model = SqoopHive2MysqlExecutions

    def get(self, request, status):
        self.paginate_by = DEFAULT_PAGE_SIEZE
        self.object_list = SqoopHive2MysqlExecutions.objects.filter(status=status).order_by('-start_time')
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Exception("Empty list and '%(class_name)s.allow_empty' is False.")
        context = self.get_context_data()
        return self.render_to_response(context)

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]


def dictfetchone(cursor):
    "Returns one row from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchone()
        ]
