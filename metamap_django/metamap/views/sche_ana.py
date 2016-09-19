# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import json

from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from rest_framework import viewsets

from metamap.djcelery_models import DjceleryCrontabschedule, DjceleryPeriodictasks
from metamap.helpers import cronhelper
from metamap.models import WillDependencyTask, PeriodicTask, AnaETL, Exports
from metamap.serializers import ExportsSerializer
from metamap.utils import httputils
from metamap.utils.constants import DEFAULT_PAGE_SIEZE


class ScheDepListView(generic.ListView):
    template_name = 'sche/ana/list.html'
    context_object_name = 'objs'
    model = WillDependencyTask

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return WillDependencyTask.objects.filter(type=2, etl__tblName__contains=tbl_name_).order_by('-valid', '-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return WillDependencyTask.objects.filter(type=2).order_by('-valid', '-ctime')

    def get_context_data(self, **kwargs):
        context = super(ScheDepListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


@transaction.atomic
def add(request):
    if request.POST:
        task = WillDependencyTask()
        httputils.post2obj(task, request.POST, 'id')
        task.type = 2
        task.schedule = 4
        task.save()

        cron_task = PeriodicTask.objects.create()
        cron_task.name = task.name
        cron_task.willtask = task
        cron_task.task = 'metamap.tasks.exec_etl_cli'
        cron_task.args = '[' + str(task.id) + ']'

        cron = DjceleryCrontabschedule.objects.create()
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(request.POST['cronexp'])
        cron_task.crontab = cron
        cron.save()

        cron_task.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()
        return redirect('export:sche_list')
    else:
        return render(request, 'sche/ana/edit.html')

class ExportsViewSet(viewsets.ModelViewSet):
    queryset = Exports.objects.all().order_by('-start_time')
    serializer_class = ExportsSerializer

@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)
        httputils.post2obj(task, request.POST, 'id')
        task.save()

        cron_task = PeriodicTask.objects.get(willtask_id=pk)
        cron_task.name = task.name
        cron_task.save()

        cron = DjceleryCrontabschedule.objects.get(pk=cron_task.crontab_id)
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
        cron.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()

        return redirect('export:sche_list')
    else:
        obj = WillDependencyTask.objects.get(pk=pk)
        return render(request, 'sche/ana/edit.html', {'task': obj})