# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import datetime
import json
import logging
import os
import traceback

from django.core.exceptions import ObjectDoesNotExist
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
from metamap.models import AnaETL, Exports, ExecObj, ExecutionsV2
from metamap.rest.serializers import ExportsSerializer, ExecutionsV2Serializer
from will_common.models import WillDependencyTask, PeriodicTask
from will_common.utils import PushUtils
from will_common.utils import constants
from will_common.utils import httputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE

logger = logging.getLogger('django')


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
            objjs = WillDependencyTask.objects.filter(type=100, name__contains=tbl_name_).order_by('-valid', '-ctime')
        else:
            self.paginate_by = DEFAULT_PAGE_SIEZE
            objjs = WillDependencyTask.objects.filter(type=100).order_by('-valid', '-ctime')
        print('count is %d ' % objjs.count())
        for tt in objjs:
            try:
                eo = ExecObj.objects.get(pk=tt.rel_id)
            except ObjectDoesNotExist, e:
                logger.error(' sche error for tt id : %id,   %s ' % (tt.id, traceback.format_exc()))
                objjs = objjs.exclude(id=tt.id)
                continue
            if eo.type != 2 or eo.cgroup_id != self.request.user.userprofile.org_group_id:
                objjs = objjs.exclude(id=tt.id)
        print('after count is %d ' % objjs.count())
        return objjs

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
        task.type = 100
        task.schedule = 4
        ana = ExecObj.objects.get(pk=task.rel_id)
        if ana.creator_id != request.user.userprofile.id:
            PushUtils.push_exact_email(ana.creator.user.email,
                                       'your schedule for %s has been changed by %s' % (ana.name, request.user.email))
        task.save()

        v1_task = WillDependencyTask()
        httputils.post2obj(v1_task, request.POST, 'id')
        v1_task.type = 2
        v1_task.schedule = 4
        v1_task.rel_id = ana.rel_id
        v1_task.save()

        cron_task = PeriodicTask.objects.create()
        cron_task.name = task.name
        cron_task.willtask = task
        cron_task.enabled = task.valid
        cron_task.task = 'metamap.tasks.exec_etl_cli2'
        cron_task.args = '[' + str(task.id) + ']'

        print('cronexppppp is %s ' %  request.POST['cronexp'])
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
    queryset = ExecutionsV2.objects.all()
    # serializer_class = ExportsSerializer
    serializer_class = ExecutionsV2Serializer

    @list_route(methods=['GET'])
    def get_file(self, request):
        from django.http import FileResponse
        filename = request.query_params['filename']
        group = request.query_params['group']
        user = request.query_params['user']
        result = 'success'
        # if group == 'xiaov' or group == 'jlc-match':
        #     result = 'success'
        # else:
        #     sid = request.query_params['sid']
        #     if group == 'jlc':
        #         result = httputils.jlc_auth(user, sid)
        if '.csv' in filename:
            final_filename = filename
        else:
            final_filename = filename + '.csv'
        full_file = constants.TMP_EXPORT_FILE_LOCATION + filename
        if not os.path.exists(full_file):
            for f in os.listdir(constants.TMP_EXPORT_FILE_LOCATION):
                path = os.path.join(constants.TMP_EXPORT_FILE_LOCATION, f)
                is_startswith = f.startswith(filename.encode('utf8'))
                if not is_startswith:
                    is_startswith = f.startswith(filename[0:-2].encode('utf8'))
                if not is_startswith:
                    is_startswith = f.startswith(filename[0:-4].encode('utf8'))
                if not os.path.isdir(path) and is_startswith and not f.endswith('.error'):
                    full_file = path
                    break
        if not os.path.exists(full_file):
            execution = ExecutionsV2.objects.get(log_location__contains=filename)
            job = execution.job
            ana = AnaETL.objects.get(id=job.rel_id)
            full_file = full_file.replace(job.name, ana.name)
            if not os.path.exists(full_file):
                filename = filename.replace(job.name, ana.name)
                for f in os.listdir(constants.TMP_EXPORT_FILE_LOCATION):
                    path = os.path.join(constants.TMP_EXPORT_FILE_LOCATION, f)
                    is_startswith = f.startswith(filename.encode('utf8'))
                    if not is_startswith:
                        is_startswith = f.startswith(filename[0:-2].encode('utf8'))
                    if not is_startswith:
                        is_startswith = f.startswith(filename[0:-4].encode('utf8'))
                    if not os.path.isdir(path) and is_startswith and not f.endswith('.error'):
                        full_file = path
                        break
        if result == 'success':
            print('going to download file %s ' % full_file)
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
            # objs = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
            objs = ExecutionsV2.objects.filter(start_time__gt=days, job__type=2).order_by('-start_time')
            result = list()
            for export in objs:
                if ExecObj.objects.filter(pk=export.job_id).count() == 1:
                    ana_etl = AnaETL.objects.get(pk=export.job.rel_id)
                    if not (user == 'admin' and group == 'jlc'):
                        if ana_etl.is_auth(user, group):
                            result.append(export)
                    else:
                        result.append(export)
                # if a deptask has been deleted, the export record should not be deleted immediately
                # if WillDependencyTask.objects.filter(pk=export.task_id).count() == 1:
                #     if export.task.type == 2:
                #         ana_id = export.task.rel_id
                #     elif export.task.type == 100:
                #         eo = ExecObj.objects.get(pk=export.task.rel_id)
                #         ana_id = eo.rel_id
                #     ana_etl = AnaETL.objects.get(pk=ana_id)
                #     if not (user == 'admin' and group == 'jlc'):
                #         if ana_etl.is_auth(user, group):
                #             result.append(export)
                #     else:
                #         result.append(export)
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response("no result for %s -> %s -> %s " % (group, user, sid))


@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)

        # TODO delete this after new version done
        origin_ana = ExecObj.objects.get(pk=task.rel_id)
        orig_sche_type = task.schedule
        httputils.post2obj(task, request.POST, 'id')
        ana = ExecObj.objects.get(pk=task.rel_id)
        # TODO This should be a normal part for some sub-classes
        if ana.creator_id != request.user.userprofile.id:
            PushUtils.push_exact_email(ana.creator.user.email,
                                       'your schedule for %s has been changed by %s' % (ana.name, request.user.email))
        task.save()

        # TODO delete this after new version done
        v1_task, created = WillDependencyTask.objects.get_or_create(rel_id=origin_ana.rel_id, type=ana.type,
                                                                    schedule=orig_sche_type)
        httputils.post2obj(v1_task, request.POST, 'id')
        v1_task.rel_id = ana.rel_id
        v1_task.type = AnaETL.type
        v1_task.save()

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
