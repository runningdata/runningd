# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import render
from django.views import generic
from djcelery.models import IntervalSchedule, CrontabSchedule

from metamap.models import ETL, PeriodicTask
from metamap.utils.constants import DEFAULT_PAGE_SIEZE


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
    return render(request, 'sche/list.html', {'etl' : etl, 'objs' : queryset})

def sche_list(request):
    queryset = PeriodicTask.objects.all()
    return render(request, 'sche/list.html', {'objs' : queryset})

def add(request, etlid=-1):
    if request.POST:
        # name = request.POST['name']
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