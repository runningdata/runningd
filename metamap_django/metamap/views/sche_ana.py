# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
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
from metamap.models import AnaETL, Exports, BIUser
from metamap.serializers import ExportsSerializer, BIUserSerializer
from will_common.models import WillDependencyTask, PeriodicTask
from will_common.utils import constants
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE


class ScheDepListView(generic.ListView):
    template_name = 'sche/ana/list.html'
    context_object_name = 'objs'
    model = WillDependencyTask

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return WillDependencyTask.objects.filter(type=2, name__contains=tbl_name_).order_by('-valid', '-ctime')
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
        cron_task.enabled = task.valid
        cron_task.task = 'metamap.tasks.exec_etl_cli'
        cron_task.args = '[' + str(task.id) + ']'

        cron = DjceleryCrontabschedule.objects.create()
        cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
            request.POST['cronexp'])
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
    now = timezone.now()
    days = now - datetime.timedelta(days=7)
    queryset = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
    serializer_class = ExportsSerializer

    @list_route(methods=['GET'])
    def get_file(self, request):
        from django.http import FileResponse
        user = request.query_params['user']
        sid = request.query_params['sid']
        filename = request.query_params['filename']
        result = httputils.jlc_auth(user, sid)
        full_file = constants.TMP_EXPORT_FILE_LOCATION + filename
        if result == 'success':
            response = FileResponse(open(full_file, 'rb'))
            response['Content-Disposition'] = 'attachment; filename=te.sh'
            return response
        else:
            return HttpResponse("session is not valid")

    @list_route(methods=['GET'])
    def get_all(self, request):
        now = timezone.now()
        days = now - datetime.timedelta(days=7)
        user = request.query_params['user']
        sid = request.query_params['sid']
        result = httputils.jlc_auth(user, sid)
        if result == 'success':
            print 'auth done'
            objs = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
            result = list()
            for export in objs:
                ana_id = export.task.rel_id
                ana_etl = AnaETL.objects.get(pk=ana_id)
                if user != 'xuexu':
                    if ana_etl.is_auth(user):
                        result.append(export)
                else:
                    result.append(export)
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response("no result")


class BIUserViewSet(viewsets.ModelViewSet):
    queryset = BIUser.objects.using('ykx_wd').all()
    serializer_class = BIUserSerializer


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
