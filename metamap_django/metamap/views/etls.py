# -*- coding: utf-8 -*
import logging
import os

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

from metamap.models import TblBlood, ETL, Executions
from metamap.utils import hivecli, httputils, dateutils, threadpool
from metamap.utils.constants import *
from metamap.utils.enums import EXECUTION_STATUS
from django.template import Context, Template

logger = logging.getLogger(__name__)
work_manager = threadpool.WorkManager(10, 3)


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'

    def get_queryset(self):
        etls = ETL.objects.filter(valid=1)
        print etls
        return etls


class EditView(generic.DetailView):
    template_name = 'etl/edit.html'
    context_object_name = 'form'
    queryset = ETL.objects.all()


# class ETLForm(forms.ModelForm):
#     preSql = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control", "size": 10}))
#
#     class Meta:
#         model = ETL
#         exclude = ['id', 'ctime']


def find_parent_mermaid(blood, final_bloods, current=0):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)


def find_child_mermaid(blood, final_bloods, current=0):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)


def blood(request, etlid):
    blood = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1).get()
    final_bloods = set()
    final_bloods.add(clean_blood(blood, etlid))
    find_parent_mermaid(blood, final_bloods, etlid)
    find_child_mermaid(blood, final_bloods, etlid)
    return render(request, 'etl/blood.html', {'bloods': final_bloods})


def clean_blood(blood, current=0):
    '''
    为了方便mermaid显示，把blood里的@替换为__
    :param blood:
    :return:
    '''
    blood.parentTbl = blood.parentTbl.replace('@', '__')
    blood.tblName = blood.tblName.replace('@', '__')
    if current > 0:
        blood.tblName += ';style ' + blood.tblName.replace('@', '__') + ' fill:#f9f,stroke:#333,stroke-width:4px'
    return blood


@transaction.atomic
def add(request):
    if request.method == 'POST':
        etl = ETL()
        httputils.post2obj(etl, request.POST, 'id')
        etl.save()
        logger.info('ETL has been created successfully : %s ' % etl)
        deps = hivecli.getTbls(etl.query)
        for dep in deps:
            tblBlood = TblBlood(tblName=etl.tblName, parentTbl=dep, relatedEtlId=etl.id)
            tblBlood.save()
            logger.info('Tblblood has been created successfully : %s' % tblBlood)
        return HttpResponseRedirect(reverse('metamap:index'))
    else:
        return render(request, 'etl/edit.html')


@transaction.atomic
def edit(request, pk):
    if request.method == 'POST':

        privious_etl = ETL.objects.filter(valid=1).get(pk=int(pk))
        privious_etl.valid = 0
        privious_etl.save()

        privious_etl.valid = 1
        privious_etl.id = None
        etl = privious_etl
        httputils.post2obj(etl, request.POST, 'id')

        etl.save()
        logger.info('ETL has been created successfully : %s ' % etl)
        deps = hivecli.getTbls(etl.query)
        for dep in deps:
            tblBlood = TblBlood(tblName=etl.tblName, parentTbl=dep, relatedEtlId=etl.id)
            tblBlood.save()
            logger.info('Tblblood has been created successfully : %s' % tblBlood)
        return HttpResponseRedirect(reverse('metamap:index'))
    else:
        etl = ETL.objects.get(pk=pk)
        return render(request, 'etl/edit.html', {'etl': etl})


@transaction.atomic
def exec_job(request, etlid):
    etl = ETL.objects.get(id=etlid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-' + etl.tblName.replace('@', '__') + '.hql'
    str = list()
    str.append('{% load etlutils %}')
    str.append(etl.variables)
    str.append("-- job for " + etl.tblName)
    str.append("-- author : " + etl.author)
    ctime = etl.ctime
    if (ctime != None):
        str.append("-- create time : " + dateutils.format_day(ctime))
    else:
        str.append("-- cannot find ctime")
    str.append("-- pre settings ")
    str.append(etl.preSql)
    str.append(etl.query)

    template = Template('\n'.join(str));
    final_result = template.render(Context())

    with open(location, 'a') as f:
        print('hql content : %s ' % final_result)
        f.write(final_result)

    log_location = location.replace('hql', 'log')
    # cmd = 'sh ' + location
    os.mknod(log_location)
    work_manager.add_job(threadpool.do_job, 'sh ' + location, log_location)
    logger.info(
        'job for %s has been executed, current pool size is %d' % (etl.tblName, work_manager.work_queue.qsize()))
    execution = Executions(logLocation=log_location, jobId=etlid, status=EXECUTION_STATUS.RUNNING)
    execution.save()
    return redirect('metamap:execlog', execid=execution.id)


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = Executions.objects.get(pk=execid)
    with open(execution.logLocation, 'r') as log:
        content = log.read().replace('\n', '<br/>')
    return render(request, 'etl/exec_log.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = Executions.objects.get(pk=execid)
    with open(execution.logLocation, 'r') as log:
        content = log.read().replace('\n', '<br/>')
    return HttpResponse(content)


def exec_list(request, jobid):
    '''
    返回指定job的所有执行记录
    :param request:
    :param jobid:
    :return:
    '''
    return render(request, 'etl/executions.html',
                  {'executions': Executions.objects.filter(jobId=jobid).order_by('-start_time')})
