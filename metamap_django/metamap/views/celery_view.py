# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import hashlib
import os

from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from djcelery.models import IntervalSchedule, CrontabSchedule

from metamap import tasks
from metamap.models import ETL, PeriodicTask
from metamap.utils import dateutils
from metamap.utils.constants import DEFAULT_PAGE_SIEZE, TMP_EXPORT_FILE_LOCATION


def get_all_tasks(request):
    all_periodic_task = PeriodicTask.objects.all()
    return HttpResponse(all_periodic_task)


def update_tasks_interval(request):
    result, create = PeriodicTask.objects.get_or_create(name='liuquan_123')
    if create:
        interval = IntervalSchedule.objects.create(every=5, period='seconds')
        interval.save()
        result.interval = interval
        result.enabled = True
        result.save()
    else:
        result.interval.every = 15
        result.interval.save()
        result.enabled = True
        result.save()
    return HttpResponse(result)


def sche_etl_list(request, etlid):
    etl = ETL.objects.get(pk=etlid)
    queryset = PeriodicTask.objects.filter(etl_id=etlid)
    return render(request, 'sche/list.html', {'etl': etl, 'objs': queryset})


def sche_list(request):
    queryset = PeriodicTask.objects.all()
    return render(request, 'sche/list.html', {'objs': queryset})


def export(request):
    if request.POST:
        header = request.POST['header']
        name = request.POST['name']
        sql = request.POST['sql']
        t = dateutils.now_datetime()
        header = header.replace(',', '\t')
        part = name + '-' + t
        location = TMP_EXPORT_FILE_LOCATION + part
        PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
        lo = unicode(PROJECT_ROOT, 'UTF-8') + location
        hql = lo + '.hql'
        with open(hql, 'w') as hf:
            hf.write(sql)
        tasks.exec_etl_cli.delay('hive -f ' + hql, header, lo)
        return redirect('export:execlog', loc=location)
    else:
        return render(request, 'export/edit.html')


def execlog(request, loc):
    return HttpResponse('<a href = "' + loc + '"> loc </a>')

@transaction.atomic
def add(request, etlid=-1):
    if request.POST:
        name = request.POST['name']
        # result, create = PeriodicTask.objects.get_or_create(name=name)
        # if create:
        #     interval = IntervalSchedule.objects.create(every=request.POST['every'], period=request.POST['seconds'])
        #     interval.save()
        #     result.interval = interval
        #     result.enabled = True
        #     result.save()
        # else:
        #     result.interval.every = 15
        #     result.interval.save()
        #     result.enabled = True
        #     result.save()
        return HttpResponse('todo')
    else:
        if etlid != -1:
            etl = ETL.objects.get(pk=etlid)
            return render(request, 'sche/edit.html', {'etl': etl})
        else:
            return render(request, 'sche/edit.html')
