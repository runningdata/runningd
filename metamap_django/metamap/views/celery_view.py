# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import hashlib
import os

from django.core.files import File
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

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

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
        lo = unicode(ROOT_PATH, 'UTF-8') + location
        hql = lo + '.hql'
        with open(hql, 'w') as hf:
            hf.write(sql)
        tasks.exec_etl_cli.delay('hive -f ' + hql, header, lo)
        return redirect('export:execlog', loc=part)
    else:
        return render(request, 'export/edit.html')


def execlog(request, loc):
    if os.path.exists(ROOT_PATH + TMP_EXPORT_FILE_LOCATION + loc + '.done'):
        result = u'<a href = "/export/' + loc + u'"> 获取文件 </a>'
        return HttpResponse(result)
    else:
        result = 'loading'
        with open(ROOT_PATH + TMP_EXPORT_FILE_LOCATION + loc + '.error', 'r') as f:
            result = f.read()
        return HttpResponse('<pre>' + result + '</pre>')

def getfile(request, filename):

    loc = ROOT_PATH + TMP_EXPORT_FILE_LOCATION + filename
    wrapper = File(file(loc))
    response = HttpResponse(wrapper, content_type='text/plain')
    t = type(filename)
    re1 = 'attachment;filename=%s.csv' % filename
    en = re1.encode('gbk')
    response['Content-Length'] = os.path.getsize(loc)
    response['Content-Encoding'] = 'gbk'
    response['Content-Disposition'] = en
    return response

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
