# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import json
import logging
import os
import traceback

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from djcelery.models import IntervalSchedule

from metamap import tasks
from metamap.models import ETL, PeriodicTask, WillDependencyTask, SqoopHive2Mysql, SqoopMysql2Hive, JarApp, ExecObj, \
    WillTaskV2
from will_common.djcelery_models import DjceleryPeriodictasks, DjceleryCrontabschedule
from will_common.helpers import cronhelper
from will_common.utils import PushUtils
from will_common.utils import dateutils
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, TMP_EXPORT_FILE_LOCATION

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

logger = logging.getLogger('django')


class ScheMultiListView(generic.ListView):
    # TODO
    template_name = 'sche/multi/list.html'
    context_object_name = 'objs'
    model = WillTaskV2

@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillTaskV2.objects.get(pk=int(pk))
        httputils.post2obj(task, request.POST, 'id', 'tasks')
        task.save()
        task.tasks.clear()
        for tid in request.POST.getlist('tasks'):
            t = ExecObj.objects.get(pk=int(tid))
            task.tasks.add(t)
        # TODO refactor This should be a normal part for some sub-classes
        cron_task = PeriodicTask.objects.get(name=task.name)
        cron_task.enabled = task.valid
        cron_task.task = 'metamap.tasks.exec_will'
        cron_task.args = '[' + str(task.id) + ']'

        cron = cron_task.crontab
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
        kw_dict = dict()
        kw_dict['name'] = task.name + '-' + cron.__str__()
        kw_dict['task'] = 'WillTaskV2'
        cron_task.kwargs = json.dumps(kw_dict)
        cron.save()
        cron_task.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()
        return redirect('metamap:sche_multi_list')
    else:
        task = WillTaskV2.objects.get(pk=int(pk))
        return render(request, 'sche/multi/edit.html', {'task': task})

@transaction.atomic
def add(request):
    if request.POST:
        task = WillTaskV2()
        httputils.post2obj(task, request.POST, 'id')
        task.save()
        for tid in request.POST.getlist('tasks'):
            t = ExecObj.objects.get(pk=int(tid))
            task.tasks.add(t)
        # TODO refactor This should be a normal part for some sub-classes

        cron_task = PeriodicTask.objects.create(name=task.name)
        cron_task.enabled = task.valid
        cron_task.queue = 'cron_multi'
        cron_task.task = 'metamap.tasks.exec_will'
        cron_task.args = '[' + str(task.id) + ']'

        cron = DjceleryCrontabschedule.objects.create()
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
        cron_task.crontab = cron
        kw_dict = dict()
        kw_dict['name'] = task.name + '-' + cron.__str__()
        kw_dict['task'] = 'WillTaskV2'
        cron_task.kwargs = json.dumps(kw_dict)
        cron.save()
        cron_task.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()
        return redirect('metamap:sche_multi_list')
    else:
        return render(request, 'sche/multi/edit.html')

