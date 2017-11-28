# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import logging
import traceback
from time import timezone

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from rest_framework import viewsets

from metamap.helpers import etlhelper
from metamap.models import AnaETL
from will_common.models import WillDependencyTask, PeriodicTask
from will_common.utils import constants
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from will_common.utils.customexceptions import RDException
from will_common.views.common import GroupListView

logger = logging.getLogger('django')


class IndexView(GroupListView):
    template_name = 'export/list.html'
    context_object_name = 'objs'
    model = AnaETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return AnaETL.objects.filter(valid=1, name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return AnaETL.objects.filter(valid=1).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


@transaction.atomic
def add(request):
    if request.method == 'POST':
        obj = AnaETL()
        httputils.post2obj(obj, request.POST, 'id')
        if AnaETL.objects.filter(name=obj.name, valid=1).count() != 0:
            raise RDException(u'命名冲突', u'已经存在同名ETL')
        userutils.add_current_creator(obj, request)
        obj.save()
        logger.info('ETL has been created successfully : %s ' % obj)
        return HttpResponseRedirect(reverse('export:index'))
    else:
        return render(request, 'export/edit.html')


def exec_job(request, pk):
    sqoop = AnaETL.objects.get(id=pk)
    from metamap import tasks
    tasks.exec_execobj.delay(sqoop.exec_obj_id, name=sqoop.name)
    return redirect('/metamap/executions/status/0/')


def get_exec_log(request, log):
    try:
        with open(constants.TMP_EXPORT_FILE_LOCATION + log + '.error') as error_file:
            content = error_file.read()
        return HttpResponse(content.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse('file not found %s ' % log)


def review_sql(request, pk):
    try:
        obj = AnaETL.objects.get(id=pk)
        hql = etlhelper.generate_sql(obj.variables, obj.query)
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def edit(request, pk):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                obj = AnaETL.objects.get(pk=int(pk))
                httputils.post2obj(obj, request.POST, 'id')
                userutils.add_current_creator(obj, request)
                obj.save()
                if obj.valid == 0:
                    task = WillDependencyTask.objects.get(type=2, rel_id=obj.id)
                    task.valid = 0
                    task.save()
                    ptask = PeriodicTask.objects.get(willtask=task)
                    if ptask.enabled != 0:
                        ptask.enabled = 0
                        ptask.save()
                return HttpResponseRedirect(reverse('export:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        obj = AnaETL.objects.get(pk=pk)
        return render(request, 'export/edit.html', {'obj': obj})
