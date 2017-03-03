# -*- coding: utf-8 -*
import json
import logging
import traceback

from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm, HiddenInput, forms, Textarea
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view

from metamap.helpers import etlhelper
from metamap.models import SourceApp, SourceAppExecutions
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE, AZKABAN_SCRIPT_LOCATION
from will_common.views.common import GroupListView

logger = logging.getLogger('django')


class IndexView(GroupListView):
    template_name = 'source/list.html'
    context_object_name = 'objs'
    model = SourceApp

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            name = self.request.GET['search']
            return SourceApp.objects.filter(valid=1, name__contains=name).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        current_group = self.request.user.groups.all()
        return SourceApp.objects.filter(valid=1).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def get_engine_type(request):
    engine = ('spark', 'hadoop', 'java')
    return HttpResponse(json.dumps(engine))


def add(request):
    if request.method == 'POST':
        try:
            form = SourceForm(-1, request.POST)
            if form.is_valid():
                form.save()
                logger.info('SourceApp for %s has been added successfully')
            else:
                form = SourceForm(request.user.userprofile.id)
                return render(request, 'source/post_edit.html', {'form': form})
            return HttpResponseRedirect(reverse('metamap:source_index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:

        form = SourceForm(request.user.userprofile.id)
        return render(request, 'source/post_edit.html', {'form': form})


class SourceForm(ModelForm):
    class Meta:
        model = SourceApp
        exclude = ['ctime']
        widgets = {
            'creator': HiddenInput(),
        }

    def __init__(self, userid, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        fs = self.fields
        for f in SourceApp._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid


def review(request, pk):
    try:
        inst = SourceApp.objects.get(pk=pk)
        hql = etlhelper.generate_sourceapp_script('xx', inst)
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)

def exec_job(request, pk):
    try:
        # from will_common.utils import dateutils
        # work_dir = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-sourceapp-sche-' + task.name
        # log = work_dir + '.log'
        # command = 'sh ' + etlhelper.generate_sourceapp_script_file(work_dir, task)
        # execution = SourceAppExecutions(logLocation=log, job_id=task.id, status=0)
        from metamap import tasks
        tasks.exec_sourceapp(pk)
        return HttpResponse('Done')
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)



def edit(request, pk):
    if request.method == 'POST':
        try:
            form = SourceForm(-1, request.POST)
            if form.is_valid():
                inst = form.save(commit=False)
                inst.id = pk
                inst.save()
                logger.info('SourceApp for %s has been deleted successfully' % (pk))
                return HttpResponseRedirect(reverse('metamap:source_index'))
            else:
                print form._errors
                form = SourceForm(request.user.userprofile.id, instance=SourceApp.objects.get(pk=pk))
            return render(request, 'source/post_edit.html', {'form': form})
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = SourceForm(request.user.userprofile.id, instance=SourceApp.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})
