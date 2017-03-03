# -*- coding: utf-8 -*
import logging
import os
import traceback

from django.core.urlresolvers import reverse
from django.forms import ModelForm, HiddenInput
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from metamap.helpers import etlhelper
from metamap.models import JarApp, JarAppExecutions
from will_common.utils import dateutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION
from will_common.views.common import GroupListView

logger = logging.getLogger('django')


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
                form.save()
                logger.info('JarApp for %s has been added successfully')
            else:
                form = JarForm(request.user.userprofile.id)
                return render(request, 'source/post_edit.html', {'form': form})
            return HttpResponseRedirect(reverse('metamap:jar_index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:

        form = JarForm(request.user.userprofile.id)
        return render(request, 'source/post_edit.html', {'form': form})


class JarForm(ModelForm):
    class Meta:
        model = JarApp
        exclude = ['ctime']
        widgets = {
            'creator': HiddenInput(),
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


def review(request, pk):
    try:
        inst = JarApp.objects.get(pk=pk)
        hql = etlhelper.generate_jarapp_script('xx', inst)
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def exec_job(request, pk):
    try:
        jar_task = JarApp.objects.get(pk=pk)
        log = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-jarapp-sche-' + jar_task.name + '.log'
        work_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/'
        command = etlhelper.generate_jarapp_script(work_dir, jar_task)
        execution = JarAppExecutions(logLocation=log, job_id=jar_task.id, status=0)
        execution.save()
        from metamap import tasks
        tasks.exec_jar.delay(command, execution.id)
        return redirect('metamap:jar_execlog', execid=execution.id)
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


def delete(request, pk):
    try:
        jar = JarApp.objects.get(pk=pk)
        jar_deleted = jar.jar_file.delete()
        deleted = jar.delete()
        logger.info('JarApp for %s has been deleted successfully' % (pk))
        return HttpResponseRedirect(reverse('metamap:jar_index'))
    except Exception, e:
        return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})


def edit(request, pk):
    if request.method == 'POST':
        try:
            form = JarForm(-1, request.POST, request.FILES)
            if form.is_valid():
                inst = form.save(commit=False)
                inst.id = pk

                # whether to delete the original file
                jar = JarApp.objects.get(pk=pk)
                if len(request.FILES) > 0:
                    jar.jar_file.delete()
                else:
                    inst.jar_file = jar.jar_file
                inst.save()
            else:
                print form._errors
                form = JarForm(request.user.userprofile.id, instance=JarApp.objects.get(pk=pk))
                return render(request, 'source/post_edit.html', {'form': form})
            logger.info('JarApp for %s has been modified successfully' % pk)
            return HttpResponseRedirect(reverse('metamap:jar_index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = JarForm(request.user.userprofile.id, instance=JarApp.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})
