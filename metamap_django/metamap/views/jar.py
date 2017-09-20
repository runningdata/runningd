# -*- coding: utf-8 -*
import logging
import os
import traceback

import shutil

import django
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm, HiddenInput, ClearableFileInput
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from metamap.helpers import etlhelper
from metamap.models import JarApp, JarAppExecutions
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION
from will_common.views.common import GroupListView

logger = logging.getLogger('django')

WORK_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/'
WORK_JAR_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/jars/'


class IndexView(GroupListView):
    template_name = 'source/jar_list.html'
    context_object_name = 'objs'
    model = JarApp

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            name = self.request.GET['search']
            return JarApp.objects.filter(valid=1, name__contains=name).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        current_group = self.request.user.groups.all()
        return JarApp.objects.filter(valid=1).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def add(request):
    if request.method == 'POST':
        try:
            form = JarForm(-1, request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    xx = form.save()
                    if form.is_zip():
                        ziputils.unzip(WORK_DIR + xx.jar_file.name, WORK_JAR_DIR + xx.name)
                    logger.info('JarApp for %s has been added successfully')
            else:
                form = JarForm(request.user.userprofile.id)
                return render(request, 'source/post_edit.html', {'form': form})
            return HttpResponseRedirect(reverse('metamap:jar_index'))
        except Exception, e:
            logger.error(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = JarForm(request.user.userprofile.id)
        return render(request, 'source/post_edit.html', {'form': form})


class JarForm(ModelForm):
    class Meta:
        model = JarApp
        exclude = ['ctime', 'rel_name', 'exec_obj']
        widgets = {
            'creator': HiddenInput(),
            'jar_file': ClearableFileInput(attrs={'multiple': True}),
        }

    def __init__(self, userid, *args, **kwargs):
        super(JarForm, self).__init__(*args, **kwargs)
        fs = self.fields
        for f in JarApp._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid

    def save(self, commit=True):
        self.instance.jar_file.name = '%s_%s' % (self.instance.name, self.instance.jar_file.name)
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            self.instance.save()
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m
        return self.instance

    def is_zip(self):
        if self.instance.jar_file:
            return self.instance.jar_file.name.endswith('.zip')
        return False


def review(request, pk):
    try:
        inst = JarApp.objects.get(pk=pk)
        hql = etlhelper.generate_jarapp_script(WORK_DIR, inst)
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def exec_job(request, pk):
    try:
        jar_task = JarApp.objects.get(pk=pk)
        from metamap import tasks
        if jar_task.exec_obj:
            tasks.exec_execobj.delay(jar_task.exec_obj_id, name=jar_task.name + dateutils.now_datetime())
        else:
            raise Exception('exec obj for jar task %s is null' % jar_task.name)
        return redirect('/metamap/executions/status/0/')
        # dd = dateutils.now_datetime()
        # log = AZKABAN_SCRIPT_LOCATION + dd + '-jarapp-sche-' + jar_task.name + '.log'
        # command = etlhelper.generate_jarapp_script(WORK_DIR, jar_task)
        # execution = JarAppExecutions(logLocation=log, job_id=jar_task.id, status=0, owner=jar_task.creator)
        # execution.save()
        # from metamap import tasks
        # tasks.exec_jar.delay(command, execution.id, name=jar_task.name + '-' + dd)
        # return redirect('metamap:jar_execlog', execid=execution.id)
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def exec_log(request, execid):
    return render(request, 'jar/exec_log.html', {'execid': execid})


def get_exec_log(request, execid):
    try:
        execution = JarAppExecutions.objects.get(pk=execid)
        with open(execution.logLocation, 'r') as log:
            content = log.read().replace('\n', '<br>')
        return HttpResponse(content)
    except IOError, e:
        return HttpResponse('')

    return HttpResponse(content)


def kill_job(reqeuset, execution_id):
    pid = JarAppExecutions.objects.get(pk=int(execution_id)).pid
    out = os.system('kill ' + pid)
    if out == 0:
        return HttpResponse('success! kill ' + pid + ' for ' + execution_id)
    else:
        return HttpResponse('failed! kill ' + pid + ' for ' + execution_id)


def delete(request, pk):
    try:
        jar = JarApp.objects.get(pk=pk)
        if jar.jar_file.name.endswith('.zip'):
            if os.path.exists(WORK_JAR_DIR + jar.name):
                shutil.rmtree(WORK_JAR_DIR + jar.name)
        jar_deleted = jar.jar_file.delete()
        deleted = jar.delete()
        logger.info('JarApp for %s has been deleted successfully' % (pk))
        return HttpResponseRedirect(reverse('metamap:jar_index'))
    except Exception, e:
        return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})


def edit(request, pk):
    if request.method == 'POST':
        try:
            form = JarForm(-1, request.POST, request.FILES, instance=JarApp.objects.get(pk=pk))
            if form.is_valid():
                with transaction.atomic():
                    inst = form.save(commit=False)
                    inst.id = pk
                    # whether to delete the original file
                    jar = JarApp.objects.get(pk=pk)
                    if len(request.FILES) > 0:
                        if form.is_zip():
                            ziputils.unzip(WORK_DIR + jar.jar_file.name, WORK_JAR_DIR + jar.name, True)
                        jar.jar_file.delete()
                    else:
                        inst.jar_file = jar.jar_file
                    inst.exec_obj = jar.exec_obj
                    inst.save()
            else:
                print form._errors
                form = JarForm(request.user.userprofile.id, instance=JarApp.objects.get(pk=pk))
                return render(request, 'source/post_edit.html', {'form': form})
            logger.info('JarApp for %s has been modified successfully' % pk)
            return HttpResponseRedirect(reverse('metamap:jar_index'))
        except Exception, e:
            print(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = JarForm(request.user.userprofile.id, instance=JarApp.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})
