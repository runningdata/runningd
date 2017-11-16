# -*- coding: utf-8 -*
import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.views import generic
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from dqms.models import DqmsCase, DqmsDatasource, DqmsRule, DqmsCheck, DqmsCheckInst, DqmsCaseInst
from dqms.serializers import DqmsDatasourceSerializer, DqmsCaseSerializer, DqmsCheckInstSerializer, \
    DqmsCaseInstSerializer
from will_common.helpers import cronhelper
from will_common.models import PeriodicTask, UserProfile
from will_common.utils import httputils
import traceback

from will_common.djcelery_models import DjceleryCrontabschedule
from will_common.djcelery_models import DjceleryPeriodictasks
from will_common.utils.constants import DEFAULT_PAGE_SIEZE

logger = logging.getLogger('django')


def todo(request):
    return HttpResponse('TODO!')

@login_required
def manager(request):
    if 'chk_name' in request.GET:
        datas = DqmsCheck.objects.filter(chk_name__contains=request.GET['chk_name'])
    else:
        datas = DqmsCheck.objects.all()
    return render(request, 'check/check_manager.html', {'objs': datas})


def edit(request):
    if 'chk_id' in request.GET:
        chk_id = long(request.GET['chk_id'])
        obj = DqmsCheck.objects.get(pk=chk_id)
        return render(request, 'check/check_edit.html', {'obj': obj})
    else:
        return render(request, 'check/check_edit.html')


def subscribe(request):
    if 'chk_id' in request.POST:
        chk_id = long(request.POST['chk_id'])
        chk = DqmsCheck.objects.get(pk=chk_id)
        user = UserProfile.objects.get(user=request.user)
        managers = chk.managers.all()
        if user in managers:
            chk.managers.remove(user)
            msg = '_dy'
        else:
            chk.managers.add(user)
            msg = '_qxdy'
        # chk.managers = managers
        chk.save()
        return HttpResponse('success' + msg)
    else:
        return HttpResponse('error')

def save(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if request.POST['id'] == '-1':
                    check = DqmsCheck()
                    origin_name = request.POST['chk_name']
                else:
                    check = DqmsCheck.objects.get(pk=request.POST['id'])
                    origin_name = check.chk_name
                httputils.post2obj(check, request.POST, 'id')
                if not check.editor_id:
                    check.creator = request.user.userprofile
                check.editor = request.user.userprofile

                case_ids = request.POST['case_ids']

                check.save()
                check.cases.clear()
                if len(case_ids) > 0:
                    for case_id in case_ids.split(','):
                        check.cases.add(DqmsCase.objects.get(pk=case_id))

                cron_task, created = PeriodicTask.objects.get_or_create(name=origin_name, queue='dqms')
                cron_task.enabled = check.valid
                cron_task.name = check.chk_name
                cron_task.task = 'dqms.tasks.exec_dqms'
                cron_task.args = '[' + str(check.id) + ']'

                if cron_task.crontab:
                    cron = cron_task.crontab
                else:
                    cron = DjceleryCrontabschedule.objects.create()
                    cron_task.crontab = cron
                cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
                    request.POST['schedule'])
                cron.save()

                cron_task.save()

                tasks = DjceleryPeriodictasks.objects.get(ident=1)
                tasks.last_update = timezone.now()
                tasks.save()
                return HttpResponseRedirect('/dqms/check')
        except Exception, e:
            logger.info(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        return render(request, 'check/check_edit.html')


def executions(request, pk):
    return render(request, 'check/executions.html', {'objs': DqmsCheckInst.objects.filter(chk_id=pk)})


def delete(request):
    if 'id' in request.POST:
        with transaction.atomic():
            case_id = int(request.POST['id'])
            case = DqmsCheck.objects.get(pk=case_id)
            case.delete()
            result = dict()
            result['msg'] = 'success'
            return JsonResponse(result)


def add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                case = DqmsCase()
                httputils.post2obj(case, request.POST, 'id')
                # case.save()
                logger.info('case has been created successfully : %s ' % case)
                return HttpResponseRedirect(reverse('dqms:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        return render(request, 'case/edit.html')


class CheckViewSet(viewsets.ModelViewSet):
    serializer_class = DqmsCaseSerializer
    queryset = DqmsCase.objects.all()

    @list_route(methods=['GET'])
    def get_all(self, request):
        chk_id = request.GET['id']
        if 'NaN' != chk_id:
            check_id = int(chk_id)
            result = DqmsCheck.objects.get(pk=check_id).cases.all()
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response('[]')


class CheckInstViewSet(viewsets.ModelViewSet):
    serializer_class = DqmsCheckInstSerializer
    queryset = DqmsCheckInst.objects.all()

    @list_route(methods=['GET'])
    def get_all(self, request):
        chk_id = request.GET['id']
        if 'NaN' != chk_id:
            check_id = int(chk_id)
            result = DqmsCheckInst.objects.filter(chk_id=check_id).order_by('-start_time')
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response('[]')


def execution(request):
    chk_id = request.GET['id']
    if 'NaN' != chk_id:
        check_id = int(chk_id)
        result = DqmsCheckInst.objects.filter(chk_id=check_id).order_by('-start_time')
        s = [obj.as_dict() for obj in result]
        rr = dict()
        rr['data'] = s
        rr['count'] = len(s)
        return JsonResponse(rr)
    else:
        return JsonResponse('[]')


class CaseInstViewSet(viewsets.ModelViewSet):
    serializer_class = DqmsCaseInstSerializer
    queryset = DqmsCaseInst.objects.all()

    @list_route(methods=['GET'])
    def get_all(self, request):
        case_id = request.GET['id']
        if 'NaN' != case_id:
            cid = int(case_id)
            result = DqmsCaseInst.objects.filter(case_id=cid).order_by('-start_time')
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        else:
            return Response('[]')
