# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
import json
import os

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from will_common.djcelery_models import DjceleryCrontabschedule, DjceleryPeriodictasks
from will_common.helpers import cronhelper
from metamap.models import AnaETL, Exports, ExecObj
from metamap.rest.serializers import ExportsSerializer
from will_common.models import WillDependencyTask, PeriodicTask
from will_common.utils import PushUtils
from will_common.utils import constants
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE


def filter_ana(objjs, obj):
    eo = ExecObj.objects.get(pk=obj.rel_id)
    # print('%s s type is %d ' % (eo.name, eo.type))
    if eo.type != 2:
        # print('%s has been excluded ' % eo.name)
        objjs.exclude(id=obj.id)
    return objjs
    # print('%objjs s count is %d ' % (objjs.count()))

class ScheDepListView(generic.ListView):
    template_name = 'sche/ana/list.html'
    context_object_name = 'objs'
    model = WillDependencyTask

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            rere = WillDependencyTask.objects.filter(type=100, name__contains=tbl_name_).order_by('-valid', '-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        rere = WillDependencyTask.objects.filter(type=100).order_by('-valid', '-ctime')
        print('count is %d ' % rere.count())
        for tt in rere:
            rere = filter_ana(rere, tt)
        print('after count is %d ' % rere.count())
        return rere

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
        ana = AnaETL.objects.get(pk=task.rel_id)
        if ana.creator_id != request.user.userprofile.id:
            PushUtils.push_exact_email(ana.creator.user.email,
                                       'your schedule for %s has been changed by %s' % (ana.name, request.user.email))
        task.save()

        cron_task = PeriodicTask.objects.create()
        cron_task.name = task.name
        cron_task.willtask = task
        cron_task.enabled = task.valid
        cron_task.task = 'metamap.tasks.exec_etl_cli'
        cron_task.args = '[' + str(task.id) + ']'

        cron = DjceleryCrontabschedule.objects.create()
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
        cron_task.crontab = cron
        cron.save()

        kw_dict = dict()
        kw_dict['name'] = task.name + '-' + cron.__str__()
        cron_task.kwargs = json.dumps(kw_dict)
        cron_task.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()
        return redirect('export:sche_list')
    else:
        return render(request, 'sche/ana/edit.html')

class ExportsViewSet(viewsets.ModelViewSet):
    now = timezone.now()
    days = now - datetime.timedelta(days=7)
    queryset = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
    serializer_class = ExportsSerializer

    @list_route(methods=['GET'])
    def get_file(self, request):
        from django.http import FileResponse
        filename = request.query_params['filename']
        group = request.query_params['group']
        user = request.query_params['user']
        if group == 'xiaov' or group == 'jlc-match':
            result = 'success'
        else:
            sid = request.query_params['sid']
            if group == 'jlc':
                result = httputils.jlc_auth(user, sid)
        final_filename = filename + '.csv'
        full_file = constants.TMP_EXPORT_FILE_LOCATION + filename
        if not os.path.exists(full_file):
            for f in os.listdir(constants.TMP_EXPORT_FILE_LOCATION):
                path = os.path.join(constants.TMP_EXPORT_FILE_LOCATION, f)
                encode_done = filename.encode('utf8')
                is_startswith = f.startswith(encode_done)
                if not os.path.isdir(path) and is_startswith and not f.endswith('.error'):
                    full_file = path
                    break
        if result == 'success':
            response = FileResponse(open(full_file, 'rb'))
            response['Content-Disposition'] = 'attachment; filename=%s' % final_filename.encode('utf-8')
            return response
        else:
            return HttpResponse("session is not valid")

    @list_route(methods=['GET'])
    def get_all(self, request):
        now = timezone.now()
        days = now - datetime.timedelta(days=7)
        group = request.query_params['group']
        user = request.query_params['user']
        if group == 'xiaov' or group == 'jlc-match':
            result = 'success'
        else:
            sid = request.query_params['sid']
            if group == 'jlc':
                result = httputils.jlc_auth(user, sid)
        if result == 'success':
            objs = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
            result = list()
            for export in objs:
                ana_id = export.task.rel_id
                ana_etl = AnaETL.objects.get(pk=ana_id)
                if user != 'xuexu':
                    if ana_etl.is_auth(user, group):
                        result.append(export)
                else:
                    result.append(export)
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response("no result for %s -> %s -> %s " % (group, user, sid))


@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)
        httputils.post2obj(task, request.POST, 'id')
        ana = AnaETL.objects.get(pk=task.rel_id)
        # TODO This should be a normal part for some sub-classes
        if ana.creator_id != request.user.userprofile.id:
            PushUtils.push_exact_email(ana.creator.user.email,
                                       'your schedule for %s has been changed by %s' % (ana.name, request.user.email))
        task.save()
        cron_task = PeriodicTask.objects.get(willtask_id=pk)
        cron_task.name = task.name

        cron = DjceleryCrontabschedule.objects.get(pk=cron_task.crontab_id)
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
        cron.save()

        kw_dict = dict()
        kw_dict['name'] = task.name + '-' + cron.__str__()
        cron_task.kwargs = json.dumps(kw_dict)
        cron_task.save()

        ptask = PeriodicTask.objects.get(willtask=pk)
        ptask.enabled = task.valid
        ptask.save()

        tasks = DjceleryPeriodictasks.objects.get(ident=1)
        tasks.last_update = timezone.now()
        tasks.save()

        return redirect('export:sche_list')
    else:
        obj = WillDependencyTask.objects.get(pk=pk)
        return render(request, 'sche/ana/edit.html', {'task': obj})
