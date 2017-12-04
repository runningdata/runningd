# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import traceback

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from metamap.helpers import etlhelper
from metamap.models import SqoopHive2Mysql, SqoopHive2MysqlExecutions, ExecObj
from will_common.decorators import my_decorator, exeception_printer
from will_common.models import WillDependencyTask
from will_common.utils import PushUtils
from will_common.utils import dateutils
from will_common.utils import encryptutils
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils import ziputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION, AZKABAN_BASE_LOCATION
from will_common.utils.customexceptions import RDException
from will_common.views.common import GroupListView

logger = logging.getLogger('info')


class Hive2MysqlListView(GroupListView):
    template_name = 'sqoop/list.html'
    context_object_name = 'objs'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            search = self.request.GET['search']
            return SqoopHive2Mysql.objects.filter(name__icontains=search).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return SqoopHive2Mysql.objects.all().order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(Hive2MysqlListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


# @exeception_printer
def add(request):
    if request.method == 'POST':
        sqoop = SqoopHive2Mysql()
        httputils.post2obj(sqoop, request.POST, 'id')
        if SqoopHive2Mysql.objects.filter(name=sqoop.name, valid=1).count() != 0:
            raise RDException(u'命名冲突', u'已经存在同名ETL')
        userutils.add_current_creator(sqoop, request)
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/h2m/')
    else:
        return render(request, 'sqoop/edit.html')


@my_decorator('pk')
def edit(request, pk):
    print('inner')
    if request.method == 'POST':
        sqoop = SqoopHive2Mysql.objects.get(pk=int(pk))
        httputils.post2obj(sqoop, request.POST, 'id')
        userutils.add_current_creator(sqoop, request)
        sqoop.save()
        logger.info('sqoop has been created successfully : %s ' % sqoop)
        return HttpResponseRedirect('/metamap/h2m/')
    else:
        obj = SqoopHive2Mysql.objects.get(pk=pk)
        return render(request, 'sqoop/edit.html', {'obj': obj})


def exec_job(request, sqoopid):
    sqoop = SqoopHive2Mysql.objects.get(id=sqoopid)
    from metamap import tasks
    if sqoop.exec_obj:
        tasks.exec_execobj.delay(sqoop.exec_obj_id, name=sqoop.name + dateutils.now_datetime())
    else:
        raise Exception('exec obj for h2m task %s is null' % sqoop.name)
    return redirect('/metamap/executions/status/0/')
    # dd = dateutils.now_datetime()
    # location = AZKABAN_SCRIPT_LOCATION + dd + '-sqoop-' + sqoop.name + '.log'
    # command = etlhelper.generate_sqoop_hive2mysql(sqoop)
    # if not settings.USE_ROOT:
    #     command = 'runuser -l ' + sqoop.cgroup.name + ' -c "' + command + '"'
    # execution = SqoopHive2MysqlExecutions(logLocation=location, job_id=sqoopid, status=0)
    # execution.save()
    # from metamap import tasks
    # tasks.exec_h2m.delay(command, location, name=sqoop.name + '-' + dd)
    # return redirect('metamap:sqoop_execlog', execid=execution.id)


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'sqoop/exec_log.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = SqoopHive2MysqlExecutions.objects.get(pk=execid)

    try:
        with open(execution.logLocation, 'r') as log:
            content = log.read().replace('\n', '<br>')
    except:
        return HttpResponse('')
    return HttpResponse(content)


def review(request, sqoop_id):
    try:
        sqoop = SqoopHive2Mysql.objects.get(id=sqoop_id)
        hql = etlhelper.generate_sqoop_hive2mysql(sqoop)
        # return render(request, 'etl/review_sql.html', {'obj': etl, 'hql': hql})
        return HttpResponse(hql.replace('--', '<br>--'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def generate_job_dag(request, schedule, group_name='xiaov'):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    current_id = 0
    try:
        folder = 'h2m-' + dateutils.now_datetime()
        leafs = WillDependencyTask.objects.filter(schedule=schedule, type=3, valid=1)
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.generate_job_file_h2m(leafs, folder, group_name)

        job_name = 'h2m_done_' + group_name + '_' + dateutils.now_datetime()
        command = 'echo done for h2m'
        deps = set()
        for leaf in leafs:
            current_id = leaf.id
            if SqoopHive2Mysql.objects.get(pk=leaf.rel_id).cgroup.name == group_name:
                deps.add(leaf.name)
        etlhelper.generate_end_job_file(job_name, command, folder, ','.join(deps))
        PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE), '%d h2m generated ' % len(leafs))
        PushUtils.push_exact_email(settings.ADMIN_EMAIL, '%d h2m generated for group %s ' % (len(deps), group_name))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s , id is %d' % (e, current_id))
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')


@permission_required('auth.admin_etl')
def restart_job(request):
    if request.method == 'POST':
        try:
            final_bloods = set()
            schedule = int(request.POST.get('schedule'))
            if schedule == 4:
                delta = dateutils.days_before_now(request.POST.get('target_day'))
                folder = 'h2m-' + dateutils.now_datetime() + '-restart-delta-' + request.POST.get('target_day')
                schedule = 0
            else:
                delta = 0
                folder = 'h2m-' + dateutils.now_datetime() + '-restart'

            os.mkdir(AZKABAN_BASE_LOCATION + folder)
            os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

            h2ms = ExecObj.objects.filter(type=3, creator__org_group__name='jlc')
            h2ms = [h2m for h2m in h2ms if WillDependencyTask.objects.filter(name=h2m.name, schedule=0).count() > 0]
            etlhelper.generate_job_file_h2m_restart(h2ms, folder, 0, delta=delta)
            etlhelper.generate_job_file_for_partition('etl_done_' + folder, [h2m.name for h2m in h2ms], folder, delta)
            task_zipfile = AZKABAN_BASE_LOCATION + folder
            ziputils.zip_dir(task_zipfile)
            return HttpResponse(folder)
        except Exception, e:
            logger.error('error : %s ' % e)
            logger.error('traceback is : %s ' % traceback.format_exc())
            return HttpResponse('error')
    else:
        return render(request, 'etl/restart.html')
