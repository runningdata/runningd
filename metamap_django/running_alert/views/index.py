# -*- coding: utf-8 -*
import logging
import traceback

from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm, HiddenInput
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic

from running_alert.models import MonitorInstance
from running_alert.pagenames import *
from will_common.models import UserProfile

logger = logging.getLogger('django')


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'objs'
    model = MonitorInstance

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return MonitorInstance.objects.filter(status=0, instance_name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = 10
        return MonitorInstance.objects.all().order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


class MonitorInstanceForm(ModelForm):
    class Meta:
        model = MonitorInstance
        exclude = ['ctime', 'utime', 'exporter_uri']
        widgets = {
            'creator': HiddenInput(),
        }

    field_order = ['cgroup', 'instance_name', 'host_and_port']

    def __init__(self, userid, *args, **kwargs):
        super(MonitorInstanceForm, self).__init__(*args, **kwargs)
        fs = self.fields
        for f in MonitorInstance._meta.fields:
            if f.name != u'id' and f.name not in self.Meta.exclude:
                fs[f.name].widget.attrs.update({'class': 'form-control'})
        if userid != -1:
            fs['creator'].initial = userid


def add(request):
    if request.method == 'POST':
        try:
            form = MonitorInstanceForm(-1, request.POST)
            if form.is_valid():
                form.save()
                logger.info('MonitorInstance for %s has been added successfully')
            else:
                form = MonitorInstanceForm(request.user.userprofile.id)
                return render(request, 'instance/edit.html', {'form': form, 'summary': JMX_ADD_SUMMARY})
            return HttpResponseRedirect(reverse('alert:index'))
        except Exception, e:
            logger.error(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = MonitorInstanceForm(request.user.userprofile.id)
        return render(request, 'instance/edit.html', {'form': form, 'summary': JMX_ADD_SUMMARY})


def subscribe(request):
    if 'obj_id' in request.POST:
        obj_id = long(request.POST['obj_id'])
        obj = MonitorInstance.objects.get(pk=obj_id)
        user = UserProfile.objects.get(user=request.user)
        msg = obj.change_subscribe_status(user)
        # obj.managers = managers
        obj.save()
        return HttpResponse('success' + msg)
    else:
        return HttpResponse('error')


def edit(request, pk):
    if request.method == 'POST':
        try:
            form = MonitorInstanceForm(-1, request.POST, instance=MonitorInstance.objects.get(pk=pk))
            if form.is_valid():
                obj = form.save(commit=False)
                obj.utime = timezone.now()
                obj.save()
            else:
                print form._errors
                form = MonitorInstanceForm(request.user.userprofile.id, instance=MonitorInstance.objects.get(pk=pk))
                return render(request, 'source/post_edit.html', {'form': form})
            logger.info('MonitorInstance for %s has been modified successfully' % pk)
            return HttpResponseRedirect(reverse('alert:index'))
        except Exception, e:
            print(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        form = MonitorInstanceForm(request.user.userprofile.id, instance=MonitorInstance.objects.get(pk=pk))
        return render(request, 'source/post_edit.html', {'form': form})
