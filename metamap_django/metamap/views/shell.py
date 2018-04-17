# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import traceback

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from metamap.models import ShellApp, ExecutionsV2
from will_common.utils import dateutils
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from will_common.utils.customexceptions import RDException
from will_common.views.common import GroupListView

logger = logging.getLogger('info')


class ShellListView(GroupListView):
    template_name = 'shell/list2.html'
    context_object_name = 'objs'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            search = self.request.GET['search']
            return ShellApp.objects.filter(name__icontains=search).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ShellApp.objects.all().order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(ShellListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def add(request):
    if request.method == 'POST':
        shell = ShellApp()
        httputils.post2obj(shell, request.POST, 'id')
        if ShellApp.objects.filter(name=shell.name, valid=1).count() != 0:
            raise RDException(u'命名冲突', u'已经存在同名ETL')
        userutils.add_current_creator(shell, request)
        shell.save()
        logger.info('shell has been created successfully : %s ' % shell)
        return HttpResponseRedirect('/metamap/shell/')
    else:
        return render(request, 'shell/edit.html')


def edit(request, pk):
    if request.method == 'POST':
        shell = ShellApp.objects.get(pk=int(pk))
        httputils.post2obj(shell, request.POST, 'id')
        userutils.add_current_creator(shell, request)
        shell.save()
        logger.info('shell has been created successfully : %s ' % shell)
        return HttpResponseRedirect('/metamap/shell/')
    else:
        obj = ShellApp.objects.get(pk=pk)
        return render(request, 'shell/edit.html', {'obj': obj})


def exec_job(request, shellid):
    shell = ShellApp.objects.get(id=shellid)
    from metamap import tasks
    if shell.exec_obj:
        tasks.exec_execobj.delay(shell.exec_obj_id, name=shell.name + dateutils.now_datetime())
    else:
        raise Exception('exec obj for shell task %s is null' % shell.name)
    return redirect('/metamap/executions/status/0/')


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'shell/exec_log2.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = ExecutionsV2.objects.get(pk=execid)

    try:
        with open(execution.logLocation, 'r') as log:
            content = log.read().replace('\n', '<br>')
    except:
        return HttpResponse('')
    return HttpResponse(content)


def review(request, shellid):
    try:
        shell = ShellApp.objects.get(id=shellid)
        return HttpResponse(shell.get_cmd().replace('--', '<br>--'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)
