# -*- coding: utf-8 -*
import logging
import traceback

from django.core.urlresolvers import reverse
from django.forms import ModelForm, HiddenInput
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from django.utils import timezone
from running_alert.models import SparkMonitorInstance
from running_alert.pagenames import SPARK_ADD_SUMMARY

logger = logging.getLogger('django')


class IndexView(generic.ListView):
    template_name = 'spark/index.html'
    context_object_name = 'objs'
    model = SparkMonitorInstance

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return SparkMonitorInstance.objects.filter(status=0, instance_name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = 10
        return SparkMonitorInstance.objects.all().order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


class SparkMonitorInstanceForm(ModelForm):
    class Meta:
        model = SparkMonitorInstance
        exclude = ['ctime', 'utime', 'exporter_uri']
        widgets = {
            'creator': HiddenInput(),
            'id': HiddenInput(),
        }

    field_order = ['cgroup', 'instance_name']

    def __init__(self, userid, *args, **kwargs):
        super(SparkMonitorInstanceForm, self).__init__(*args, **kwargs)
        fs = self.fields
        for f in SparkMonitorInstance._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid


def add(request):
    if request.method == 'POST':
        try:
            form = SparkMonitorInstanceForm(-1, request.POST)
            if form.is_valid():
                form.save()
                logger.info('SparkMonitorInstance for %s has been added successfully')
            else:
                form = SparkMonitorInstanceForm(request.user.userprofile.id)
                return render(request, 'instance/edit.html', {'form': form, 'summary': SPARK_ADD_SUMMARY})
            return HttpResponseRedirect(reverse('alert:spark_index'))
        except Exception, e:
            logger.error(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = SparkMonitorInstanceForm(request.user.userprofile.id)
        return render(request, 'instance/edit.html', {'form': form, 'summary': SPARK_ADD_SUMMARY})


def edit(request, pk):
    if request.method == 'POST':
        try:
            form = SparkMonitorInstanceForm(-1, request.POST, instance=SparkMonitorInstance.objects.get(pk=pk))
            if form.is_valid():
                obj = form.save(commit=False)
                obj.utime = timezone.now()
                obj.save()
            else:
                print form._errors
                form = SparkMonitorInstanceForm(request.user.userprofile.id,
                                                instance=SparkMonitorInstance.objects.get(pk=pk))
                return render(request, 'source/post_edit.html', {'form': form})
            logger.info('SparkMonitorInstance for %s has been modified successfully' % pk)
            return HttpResponseRedirect(reverse('alert:spark_index'))
        except Exception, e:
            print(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = SparkMonitorInstanceForm(request.user.userprofile.id, instance=SparkMonitorInstance.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})
