# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import logging
import traceback

import django
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import HiddenInput
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

import metamap
from metamap.helpers import etlhelper
from metamap.models import AnaETL
from will_common.models import WillDependencyTask, PeriodicTask
from will_common.utils import constants
from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from will_common.views.common import GroupListView

logger = logging.getLogger('django')


class AnaETLForm(ModelForm):
    class Meta:
        model = AnaETL
        exclude = ['ctime', 'utime', 'priority', 'valid', 'exec_obj', 'rel_name', 'author']
        widgets = {
            'creator': HiddenInput(),
            'id': HiddenInput(),
        }

    field_order = ['name', 'cgroup', 'data_source']

    def __init__(self, userid, *args, **kwargs):
        super(AnaETLForm, self).__init__(*args, **kwargs)
        fs = self.fields
        self.fields['data_source'] = django.forms.ModelChoiceField(
            queryset=metamap.models.DataMeta.objects.filter(cgroup__name='jlc'), to_field_name='id')
        for f in AnaETL._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid


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
    # if request.method == 'POST':
    #     obj = AnaETL()
    #     httputils.post2obj(obj, request.POST, 'id')
    #     if AnaETL.objects.filter(name=obj.name, valid=1).count() != 0:
    #         raise RDException(u'命名冲突', u'已经存在同名ETL')
    #     userutils.add_current_creator(obj, request)
    #     obj.save()
    #     logger.info('ETL has been created successfully : %s ' % obj)
    #     return HttpResponseRedirect(reverse('export:index'))
    # else:
    #     return render(request, 'export/edit.html')
    if request.method == 'POST':
        try:
            form = AnaETLForm(-1, request.POST)
            if form.is_valid():
                form.save()
                logger.info('AnaETL for %s has been added successfully' % form.instance.name)
            else:
                print('not valid')
                return render(request, 'export/post_edit.html', {'form': form})
            return HttpResponseRedirect(reverse('export:index'))
        except Exception, e:
            logger.error(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = AnaETLForm(request.user.userprofile.id)
        return render(request, 'export/post_edit.html', {'form': form})


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
    # if request.method == 'POST':
    #     try:
    #         with transaction.atomic():
    #             obj = AnaETL.objects.get(pk=int(pk))
    #             httputils.post2obj(obj, request.POST, 'id')
    #             userutils.add_current_creator(obj, request)
    #             obj.save()
    #             if obj.valid == 0:
    #                 task = WillDependencyTask.objects.get(type=2, rel_id=obj.id)
    #                 task.valid = 0
    #                 task.save()
    #                 ptask = PeriodicTask.objects.get(willtask=task)
    #                 if ptask.enabled != 0:
    #                     ptask.enabled = 0
    #                     ptask.save()
    #             return HttpResponseRedirect(reverse('export:index'))
    #     except Exception, e:
    #         return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    # else:
    #     obj = AnaETL.objects.get(pk=pk)
    #     return render(request, 'export/edit.html', {'obj': obj})
    if request.method == 'POST':
        form = AnaETLForm(-1, request.POST, instance=AnaETL.objects.get(pk=pk))
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
        else:
            print form._errors
            form = AnaETLForm(request.user.userprofile.id,
                              instance=AnaETL.objects.get(pk=pk))
            return render(request, 'export/post_edit.html', {'form': form})
        logger.info('shell has been created successfully : %s ' % form.instance.name)
        return HttpResponseRedirect(reverse('export:index'))
    else:
        form = AnaETLForm(request.user.userprofile.id, instance=AnaETL.objects.get(pk=pk))
        return render(request, 'export/post_edit.html', {'form': form})