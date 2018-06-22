# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import traceback

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import HiddenInput, ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone

from metamap.models import ShellApp, ExecutionsV2
from will_common.utils import dateutils
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from will_common.utils.customexceptions import RDException
from will_common.views.common import GroupListView

logger = logging.getLogger('info')


class ShellAppForm(ModelForm):
    class Meta:
        model = ShellApp
        exclude = ['ctime', 'utime', 'priority', 'valid', 'exec_obj', 'rel_name']
        widgets = {
            'creator': HiddenInput(),
            'id': HiddenInput(),
        }

    field_order = ['cgroup', 'name', 'content', 'variables']

    def __init__(self, userid, *args, **kwargs):
        super(ShellAppForm, self).__init__(*args, **kwargs)
        fs = self.fields
        for f in ShellApp._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid


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
        try:
            form = ShellAppForm(-1, request.POST)
            if form.is_valid():
                form.save()
                logger.info('ShellApp for %s has been added successfully' % form.name)
            else:
                form = ShellAppForm(request.user.userprofile.id)
                return render(request, 'source/post_edit.html', {'form': form})
            return HttpResponseRedirect('/metamap/shell/')
        except Exception, e:
            logger.error(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = ShellAppForm(request.user.userprofile.id)
        return render(request, 'source/post_edit.html', {'form': form})


def edit(request, pk):
    if request.method == 'POST':
        form = ShellAppForm(-1, request.POST, instance=ShellApp.objects.get(pk=pk))
        if form.is_valid():
            obj = form.save(commit=False)
            obj.utime = timezone.now()
            obj.save()
        else:
            print form._errors
            form = ShellAppForm(request.user.userprofile.id,
                                instance=ShellApp.objects.get(pk=pk))
            return render(request, 'source/post_edit.html', {'form': form})
        logger.info('shell has been created successfully : %s ' % form.instance.name)
        return HttpResponseRedirect('/metamap/shell/')
    else:
        form = ShellAppForm(request.user.userprofile.id, instance=ShellApp.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})


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
