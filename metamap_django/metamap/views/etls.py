# -*- coding: utf-8 -*
import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

from metamap.helpers import bloodhelper, etlhelper
from metamap.models import TblBlood, ETL, Executions
from metamap.utils import hivecli, httputils, dateutils, threadpool, ziputils
from metamap.utils.constants import *
from metamap.utils.enums import EXECUTION_STATUS

logger = logging.getLogger(__name__)
work_manager = threadpool.WorkManager(10, 3)


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'
    model = ETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ETL.objects.filter(valid=1, tblName__contains=tbl_name_)
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ETL.objects.filter(valid=1)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


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



def blood(request, etlid):
    blood = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1).get()
    final_bloods = set()
    final_bloods.add(bloodhelper.clean_blood(blood, etlid))
    bloodhelper.find_parent_mermaid(blood, final_bloods, etlid)
    bloodhelper.find_child_mermaid(blood, final_bloods, etlid)
    return render(request, 'etl/blood.html', {'bloods': final_bloods})


def blood_by_name(request):
    etl_name = request.GET['tblName']
    try:
        etl = ETL.objects.filter(valid=1).get(tblName=etl_name)
        return blood(request, etl.id)
    except ObjectDoesNotExist:
        return HttpResponse(u'%s 不存在' % etl_name)


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
    etlhelper.generate_etl_file(etl, location)
    log_location = location.replace('hql', 'log')
    os.mknod(log_location)
    work_manager.add_job(threadpool.do_job, 'sh ' + location, log_location)
    logger.info(
        'job for %s has been executed, current pool size is %d' % (etl.tblName, work_manager.work_queue.qsize()))
    execution = Executions(logLocation=log_location, job_id=etlid, status=EXECUTION_STATUS.RUNNING)
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


class ExecLogView(generic.ListView):
    '''
    返回指定job的所有执行记录
    :param jobid:
    :return:
    '''
    template_name = 'etl/executions.html'
    context_object_name = 'executions'
    model = Executions
    paginate_by = DEFAULT_PAGE_SIEZE

    def get_queryset(self):
        jobid_ = self.kwargs['jobid']
        return Executions.objects.filter(job_id=jobid_).order_by('-start_time')


def generate_job_dag(request):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        done_blood = set()
        folder = dateutils.now_datetime()
        leafs = TblBlood.objects.raw("select a.* from "
                                     + "(select * from metamap_tblblood where valid = 1) a"
                                     + " left outer join "
                                     + "(select distinct parent_tbl from metamap_tblblood where valid = 1) b"
                                     + " on a.tbl_name = b.parent_tbl"
                                     + " where b.parent_tbl is null")
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.load_nodes(leafs, folder, done_blood)
        tbl = TblBlood(tblName='etl_done_' + folder)
        etlhelper.generate_job_file(tbl, leafs, folder)
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(dateutils.now_datetime())
    except Exception, e:
        logger.error('error : %s ' % e)
        return HttpResponse('error')
