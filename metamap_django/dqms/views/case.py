# -*- coding: utf-8 -*
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from rest_framework import viewsets

from dqms import tasks
from dqms.models import DqmsCase, DqmsDatasource, DqmsRule, DqmsCaseInst
from dqms.serializers import DqmsDatasourceSerializer, DqmsCaseSerializer
from will_common.utils import httputils
import traceback

from will_common.utils import mysqlcli
from will_common.utils.constants import DEFAULT_PAGE_SIEZE

logger = logging.getLogger('django')


def todo(request):
    return HttpResponse('TODO!')

def test(request):
    result = mysqlcli.execute('dqms_check', 'select * from sys_channels')
    return JsonResponse(result)

def manager(request):
    datas = DqmsCase.objects.all()
    if 'case_name' in request.GET:
        datas = DqmsCase.objects.filter(case_name__contains=request.GET['case_name'])
    else:
        datas = DqmsCase.objects.all()
    return render(request, 'case/case_manager.html', {'objs': datas})




class CaseView(generic.ListView):
    template_name = 'case/case_manager.html'
    paginate_by = DEFAULT_PAGE_SIEZE
    model = DqmsCase
    context_object_name = 'objs'
    search_key = 'case_name'

    def get_queryset(self):
        key = self.get_key()
        if key and len(key) > 0:
            return DqmsCase.objects.filter(case_name__contains=key)
        return DqmsCase.objects.all().order_by('-ctime')

    def get_key(self):
        if self.search_key in self.request.session:
            key = self.request.session[self.search_key]
            if self.search_key in self.request.GET:
                key = self.request.GET[self.search_key]
                self.request.session[self.search_key] = key
        elif self.search_key in self.request.GET:
            key = self.request.GET[self.search_key]
            self.request.session[self.search_key] = key
        else:
            key = None
        return key


def edit(request):
    if 'case_id' in request.GET:
        cid = long(request.GET['case_id'])
        obj = DqmsCase.objects.get(pk=cid)
        return render(request, 'case/case_edit.html', {'obj': obj})
    else:
        return render(request, 'case/case_edit.html')


def save(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if request.POST['id'] == '-1':
                    case = DqmsCase()
                else:
                    case = DqmsCase.objects.get(pk=request.POST['id'])
                httputils.post2obj(case, request.POST, 'id')
                if not case.editor_id:
                    case.creator = request.user.userprofile
                case.editor = request.user.userprofile
                case.save()

                if request.POST['id'] != '-1':
                    logger.info('this is not a new case, delete all rules before')
                    case.dqmsrule_set.all().delete()

                rules = ''.join(request.POST['ruleIndexs']).split(',')
                for rule_str in rules:
                    rule = DqmsRule()
                    for kv in rule_str.split('^'):
                        if '=' not in kv:
                            continue
                        index = kv.index('=')
                        key = kv[0: index]
                        value = kv[index + 1:]
                        logger.info('going to handle %s : %s' % (key, value))
                        if hasattr(rule, key) and len(value) > 0:
                            value = ''.join(value)
                            setattr(rule, key, value)
                        rule.rule_type = 1
                    rule.case_id = case.id
                    rule.save()
                logger.info('case has been created successfully : %s ' % case)
                return HttpResponseRedirect('/dqms/case')
        except Exception, e:
            logger.info(traceback.format_exc())
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        return render(request, 'case/case_edit.html')

def runtest(request, pk):
    tasks.run_case(pk, request.user.id)
    result = dict()
    result['msg'] = 'success'
    return JsonResponse(result)

def delete(request):
    if 'id' in request.POST:
        with transaction.atomic():
            case_id = int(request.POST['id'])
            case = DqmsCase.objects.get(pk=case_id)
            case.delete()
            result = dict()
            result['msg'] = 'success'
            return JsonResponse(result)

def add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                case = DqmsCase()
                httputils.post2obj(case, request.POST, 'id')
                # case.save()
                logger.info('case has been created successfully : %s ' % case)
                return HttpResponseRedirect(reverse('dqms:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        return render(request, 'case/edit.html')


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'objs'
    model = DqmsCase

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return DqmsCase.objects.filter(status=0, case_name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = 10
        return DqmsCase.objects.filter(status=0).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


class DataSrcViewSet(viewsets.ModelViewSet):
    queryset = DqmsDatasource.objects.all()
    serializer_class = DqmsDatasourceSerializer


def execution(request):
    chk_id = request.GET['id']
    if 'NaN' != chk_id:
        check_id = int(chk_id)
        result = DqmsCaseInst.objects.filter(case_id=check_id).order_by('-start_time')
        s = [obj.as_dict() for obj in result]
        rr = dict()
        rr['data'] = s
        rr['count'] = len(s)
        return JsonResponse(rr)
    else:
        return JsonResponse('[]')

class CaseViewSet(viewsets.ModelViewSet):
    queryset = DqmsCase.objects.all()
    serializer_class = DqmsCaseSerializer
