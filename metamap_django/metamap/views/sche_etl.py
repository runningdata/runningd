# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import os

from django.core.files import File
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from djcelery.models import IntervalSchedule

from metamap import tasks
from metamap.models import ETL, PeriodicTask, WillDependencyTask
from will_common.utils import dateutils
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, TMP_EXPORT_FILE_LOCATION

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
    queryset = WillDependencyTask.objects.filter(rel_id=etlid, type=1)
    return render(request, 'sche/list.html', {'objs': queryset, 'etl': etl})


class ScheDepListView(generic.ListView):
    template_name = 'sche/list.html'
    context_object_name = 'objs'
    model = WillDependencyTask

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            objs = WillDependencyTask.objects.filter(type=1, name__contains=tbl_name_).order_by('-valid', '-ctime')
            for obj in objs:
                pk = obj.rel_id
                etl = ETL.objects.get(id=pk)
                if etl.valid != 1:
                    objs = objs.exclude(id=obj.id)
            return objs
        self.paginate_by = DEFAULT_PAGE_SIEZE
        objs = WillDependencyTask.objects.filter(type=1).order_by('-valid', '-ctime')
        for obj in objs:
            pk = obj.rel_id
            etl = ETL.objects.get(id=pk)
            if etl.valid != 1:
                objs = objs.exclude(id=obj.id)
        return objs

    def get_context_data(self, **kwargs):
        context = super(ScheDepListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def sche_cron_list(request):
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
    en = re1.encode('utf-8')
    response['Content-Length'] = os.path.getsize(loc)
    response['Content-Encoding'] = 'utf-8'
    response['Content-Disposition'] = en
    return response


@transaction.atomic
def add(request):
    if request.POST:
        task = WillDependencyTask()
        httputils.post2obj(task, request.POST, 'id')
        task.save()
        return redirect('metamap:sche_list')
    else:
        return render(request, 'sche/edit.html')


@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)
        httputils.post2obj(task, request.POST, 'id')
        task.save()
        return redirect('metamap:sche_list')
    else:
        obj = WillDependencyTask.objects.get(pk=pk)
        return render(request, 'sche/edit.html', {'task': obj})


@transaction.atomic
def migrate_jobs(request):
    etls = ETL.objects.filter(valid=1, onSchedule=1)
    for etl in etls:
        WillDependencyTask.objects.get_or_create(schedule=0, etl_id=etl.id, name=etl.tblName, variables=etl.variables)
    return HttpResponse('success')
