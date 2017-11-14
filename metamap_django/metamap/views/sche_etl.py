# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import json
import os

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from djcelery.models import IntervalSchedule

from metamap import tasks
from metamap.models import ETL, PeriodicTask, WillDependencyTask, SqoopHive2Mysql, SqoopMysql2Hive, JarApp, WillTaskV2
from will_common.djcelery_models import DjceleryPeriodictasks, DjceleryCrontabschedule
from will_common.helpers import cronhelper
from will_common.utils import PushUtils
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

    def handle_etl(self, objss, obj):
        '''
        过滤掉无效的ETL
        :param obj:
        :return:
        '''
        try:
            etl = ETL.objects.get(id=obj.rel_id)
        except Exception, e:
            print('etl %d not found' % obj.rel_id)
            objss = objss.exclude(id=obj.id)
            return objss
        if etl.valid != 1:
            objss = objss.exclude(id=obj.id)
        return objss

    def handle_pass(self, objss, obj):
        return objss

    # TODO 考虑一下是否合适
    def handle_email_export(self, objss, obj):
        '''
        暂时不显示export的调度
        :param objss:
        :param obj:
        :return:
        '''
        objss = objss.exclude(id=obj.id)
        return objss

    def get_queryset(self):
        filters = {1: self.handle_etl, 2: self.handle_email_export, 3: self.handle_pass,
                   4: self.handle_pass, 5: self.handle_pass, 6: self.handle_pass, 100: self.handle_pass}

        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            objs = WillDependencyTask.objects.filter(name__icontains=tbl_name_).order_by('-valid', '-ctime')
            for obj in objs:
                objs = filters.get(obj.type)(objs, obj)
            return objs
        self.paginate_by = DEFAULT_PAGE_SIEZE
        objs = WillDependencyTask.objects.order_by('-valid', '-ctime')

        for obj in objs:
            objs = filters.get(obj.type)(objs, obj)
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
        # TODO refactor This should be a normal part for some sub-classes
        try:
            if int(task.type) == 1:
                etl = ETL.objects.get(pk=task.rel_id)
            elif int(task.type) == 3:
                etl = SqoopHive2Mysql.objects.get(pk=task.rel_id)
            elif int(task.type) == 4:
                etl = SqoopMysql2Hive.objects.get(pk=task.rel_id)
            elif int(task.type) == 6:
                etl = JarApp.objects.get(pk=task.rel_id)
            else:
                PushUtils.push_exact_email(settings.ADMIN_EMAIL,
                                           'task %s has no type, its type is : %d ' % (task.name, task.type))
                etl = None
            if etl and etl.creator_id != request.user.userprofile.id:
                PushUtils.push_exact_email(etl.creator.user.email,
                                           'your schedule for %s has been changed by %s' % (
                                           etl.name, request.user.email))
        except:
            print('error happens for %s scheduel ' % task.name)

        task.save()

        if int(task.schedule) == 4:
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
            kw_dict = dict()
            kw_dict['name'] = task.name + '-' + cron.__str__()
            cron_task.kwargs = json.dumps(kw_dict)
            cron.save()
            cron_task.save()

            tasks = DjceleryPeriodictasks.objects.get(ident=1)
            tasks.last_update = timezone.now()
            tasks.save()
        return redirect('metamap:sche_list')
    else:
        return render(request, 'sche/edit.html')



@transaction.atomic
def edit(request, pk):
    '''
    如果是定时任务，新建或更新定时任务与定时器
    如果不是定时任务，删掉既有的定时任务与定时器
    只要跟定时任务有关，就更新出发定时器的机关
    :param request:
    :param pk:
    :return:
    '''
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)
        orig_sche_type = task.schedule
        httputils.post2obj(task, request.POST, 'id')
        if task.type == 1 and ETL.objects.get(pk=task.rel_id).valid != 1:
            raise Exception('the etl you choose is invalid now, please rechoose another one')
        # TODO refactor This should be a normal part for some sub-classes
        try:
            if int(task.type) == 1:
                etl = ETL.objects.get(pk=task.rel_id)
            elif int(task.type) == 3:
                etl = SqoopHive2Mysql.objects.get(pk=task.rel_id)
            elif int(task.type) == 4:
                etl = SqoopMysql2Hive.objects.get(pk=task.rel_id)
            elif int(task.type) == 6:
                etl = JarApp.objects.get(pk=task.rel_id)
            else:
                PushUtils.push_exact_email(settings.ADMIN_EMAIL,
                                           'task %s has no type, its type is : %d ' % (task.name, task.type))
                etl = None
            if etl and etl.creator_id != request.user.userprofile.id:
                PushUtils.push_exact_email(etl.creator.user.email,
                                           'your schedule for %s has been changed by %s' % (
                                           etl.name, request.user.email))
        except:
            print('error happens for %s scheduel ' % task.name)
        task.save()
        if int(task.schedule) == 4:
            if PeriodicTask.objects.filter(willtask_id=pk).exists():
                cron_task = PeriodicTask.objects.get(willtask_id=pk)
                cron_task.name = task.name
                cron_task.enabled = task.valid

                cron = DjceleryCrontabschedule.objects.get(pk=cron_task.crontab_id)
                cron.minute, cron.hour, cron.day_of_month, cron.month_of_year, cron.day_of_week = cronhelper.cron_from_str(
                    request.POST['cronexp'])

                kw_dict = dict()
                kw_dict['name'] = task.name + '-' + cron.__str__()
                cron_task.kwargs = json.dumps(kw_dict)

                cron_task.save()
                cron.save()
            else:
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

        else:
            if PeriodicTask.objects.filter(willtask_id=pk).exists():
                cron_task = PeriodicTask.objects.get(willtask_id=pk)
                cronid = cron_task.crontab_id
                cron_task.delete()
                if DjceleryCrontabschedule.objects.filter(pk=cronid).exists():
                    cron = DjceleryCrontabschedule.objects.get(pk=cronid)
                    cron.delete()

        if int(orig_sche_type) == 4 or int(task.schedule) == 4:
            tasks = DjceleryPeriodictasks.objects.get(ident=1)
            tasks.last_update = timezone.now()
            tasks.save()

        return redirect('metamap:sche_list')
    else:
        obj = WillDependencyTask.objects.get(pk=pk)
        return render(request, 'sche/edit.html', {'task': obj})


@transaction.atomic
def migrate_jobs(request):
    etls = ETL.objects.filter(valid=1, onSchedule=1)
    for etl in etls:
        WillDependencyTask.objects.get_or_create(schedule=0, etl_id=etl.id, name=etl.name, variables=etl.variables)
    return HttpResponse('success')
