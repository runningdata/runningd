# -*- coding: utf-8 -*
import json
import logging
import os
import traceback

from StringIO import StringIO
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from rest_framework import routers

from metamap.helpers import bloodhelper, etlhelper
from metamap.models import TblBlood, ETL, Executions
from metamap.utils import hivecli, httputils, dateutils, ziputils
from metamap.utils.constants import *

logger = logging.getLogger('django')


# work_manager = threadpool.WorkManager(10, 3)


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'
    model = ETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ETL.objects.filter(valid=1, tblName__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ETL.objects.filter(valid=1).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


from rest_framework import routers, serializers, viewsets


class ETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ETL
        fields = ('tblName', 'valid', 'id')


class ETLViewSet(viewsets.ModelViewSet):
    queryset = ETL.objects.filter(valid=1).order_by('-ctime')
    serializer_class = ETLSerializer


router = routers.DefaultRouter()
router.register(r'etls', ETLViewSet)


def get_json(request):
    queryset = ETL.objects.filter(valid=1).order_by('-ctime')
    io = StringIO()
    json.dump(queryset, io)
    from django.core import serializers
    data = serializers.serialize('json', queryset)
    return HttpResponse(data, mimetype="application/json")


class InvalidView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'
    model = ETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ETL.objects.filter(valid=0, tblName__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ETL.objects.filter(valid=0).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(InvalidView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


class StatusJobView(generic.ListView):
    template_name = 'etl/executions_status.html'
    context_object_name = 'executions'
    model = Executions

    def get(self, request, status):
        self.paginate_by = DEFAULT_PAGE_SIEZE
        self.object_list = Executions.objects.filter(status=status).order_by('-start_time')
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Exception("Empty list and '%(class_name)s.allow_empty' is False.")
        context = self.get_context_data()
        return self.render_to_response(context)


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



def blood_dag(request, etlid):
    bloods = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1)
    final_bloods = set()
    for blood in bloods:
        final_bloods.add(bloodhelper.clean_blood(blood, etlid))
        bloodhelper.find_parent_mermaid(blood, final_bloods, etlid)
        bloodhelper.find_child_mermaid(blood, final_bloods, etlid)
    return render(request, 'etl/blood.html', {'bloods': final_bloods})


def blood_by_name(request):
    etl_name = request.GET['tblName']
    try:
        etl = ETL.objects.filter(valid=1).get(tblName=etl_name)
        return blood_dag(request, etl.id)
    except ObjectDoesNotExist:
        message = u'%s 不存在' % etl_name
        return render(request, 'common/message.html', {'message': message})


def his(request, tblName):
    etls = ETL.objects.filter(tblName=tblName).order_by('-ctime')
    return render(request, 'etl/his.html', {'etls': etls, 'tblName': tblName})


@transaction.atomic
def add(request):
    if request.method == 'POST':
        etl = ETL()
        httputils.post2obj(etl, request.POST, 'id')
        find_ = etl.tblName.find('@')
        etl.meta = etl.tblName[0: find_]
        etl.save()
        logger.info('ETL has been created successfully : %s ' % etl)
        try:
            deps = hivecli.getTbls(etl)
            for dep in deps:
                tblBlood = TblBlood(tblName=etl.tblName, parentTbl=dep, relatedEtlId=etl.id)
                tblBlood.save()
                logger.info('Tblblood has been created successfully : %s' % tblBlood)
            return HttpResponseRedirect(reverse('metamap:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': e})
    else:
        return render(request, 'etl/edit.html')


def edit(request, pk):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                privious_etl = ETL.objects.get(pk=int(pk))
                privious_etl.valid = 0
                privious_etl.save()

                deleted, rows = TblBlood.objects.filter(relatedEtlId=pk).delete()
                logger.info('Tblbloods for %s has been deleted successfully' % (pk))

                if int(request.POST['valid']) == 1:
                    etl = privious_etl
                    privious_etl.id = None
                    privious_etl.ctime = timezone.now()
                    httputils.post2obj(etl, request.POST, 'id')
                    find_ = etl.tblName.find('@')
                    etl.meta = etl.tblName[0: find_]

                    etl.save()
                    logger.info('ETL has been created successfully : %s ' % etl)
                    deps = hivecli.getTbls(etl)
                    for dep in deps:
                        tblBlood = TblBlood(tblName=etl.tblName, parentTbl=dep, relatedEtlId=etl.id)
                        tblBlood.save()
                        logger.info('Tblblood has been created successfully : %s' % tblBlood)

                return HttpResponseRedirect(reverse('metamap:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        etl = ETL.objects.get(pk=pk)
        return render(request, 'etl/edit.html', {'etl': etl})


@transaction.atomic
def exec_job(request, etlid):
    etl = ETL.objects.get(id=etlid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-' + etl.tblName.replace('@', '__') + '.hql'
    etlhelper.generate_etl_file(etl, location)
    log_location = location.replace('hql', 'log')
    with open(log_location, 'a') as log:
        with open(location, 'r') as hql:
            log.write(hql.read())
    # work_manager.add_job(threadpool.do_job, 'hive -f ' + location, log_location)
    # logger.info(
    #     'job for %s has been executed, current pool size is %d' % (etl.tblName, work_manager.work_queue.qsize()))
    execution = Executions(logLocation=log_location, job_id=etlid, status=0)
    execution.save()
    from metamap import tasks
    tasks.exec_etl.delay('hive -f ' + location, log_location)
    return redirect('metamap:execlog', execid=execution.id)
    # return redirect('metamap:execlog', execid=1)

def review_sql(request, etlid):
    try:
        etl = ETL.objects.get(id=etlid)
        hql = etlhelper.generate_etl_sql(etl)
        # return render(request, 'etl/review_sql.html', {'obj': etl, 'hql': hql})
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def xx(request):
    from metamap.tasks import xx
    return HttpResponse(xx.delay())


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
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
        content = log.read().replace('\n', '<br>')
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


def preview_job_dag(request):
    try:
        bloods = TblBlood.objects.filter(valid=1).all()
        return render(request, 'etl/blood.html', {'bloods': bloods})
    except Exception, e:
        logger.error('error : %s ' % e)
        return HttpResponse('error')


def generate_job_dag(request, schedule):
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
                                     + " join "
                                     + " (select etl_id from metamap_willdependencytask where schedule=" + schedule + " and valid=1) s "
                                     + " on s.etl_id = a.related_etl_id"
                                     + " left outer join "
                                     + "(select distinct parent_tbl from metamap_tblblood where valid = 1) b"
                                     + " on a.tbl_name = b.parent_tbl"
                                     + " where b.parent_tbl is null")
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.load_nodes(leafs, folder, done_blood, schedule)
        tbl = TblBlood(tblName='etl_done_' + folder)
        etlhelper.generate_job_file(tbl, leafs, folder)
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')
