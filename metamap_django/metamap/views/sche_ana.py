# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.db import transaction
from django.shortcuts import render, redirect
from django.views import generic

from metamap.models import WillDependencyTask
from metamap.utils import httputils
from metamap.utils.constants import DEFAULT_PAGE_SIEZE


class ScheDepListView(generic.ListView):
    template_name = 'sche/ana/list.html'
    context_object_name = 'objs'
    model = WillDependencyTask

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return WillDependencyTask.objects.filter(type=2, etl__tblName__contains=tbl_name_).order_by('-valid', '-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return WillDependencyTask.objects.filter(type=2).order_by('-valid', '-ctime')

    def get_context_data(self, **kwargs):
        context = super(ScheDepListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


@transaction.atomic
def add(request):
    if request.POST:
        task = WillDependencyTask()
        httputils.post2obj(task, request.POST, 'id')
        task.type = 2
        task.save()
        return redirect('export:sche_list')
    else:
        return render(request, 'sche/ana/edit.html')


@transaction.atomic
def edit(request, pk):
    if request.POST:
        task = WillDependencyTask.objects.get(pk=pk)
        httputils.post2obj(task, request.POST, 'id')
        task.save()
        return redirect('export:sche_list')
    else:
        obj = WillDependencyTask.objects.get(pk=pk)
        return render(request, 'sche/ana/edit.html', {'task': obj})