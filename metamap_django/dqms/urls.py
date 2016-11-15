from django.conf.urls import url, include
from rest_framework import routers

from dqms.views import alert
from dqms.views import case
from dqms.views import check
from dqms.views.case import DataSrcViewSet, CaseViewSet
from dqms.views.check import CheckViewSet, CheckInstViewSet, CaseInstViewSet
from dqms.views.rule import RuleViewSet

app_name = 'dqms'

router = routers.DefaultRouter()
router.register(r'datasrc', DataSrcViewSet)
router.register(r'getcase', CaseViewSet)
router.register(r'ruleforcase', RuleViewSet)
router.register(r'caseforcheck', CheckViewSet)
router.register(r'execforcheck', CheckInstViewSet)
router.register(r'execforcase', CaseInstViewSet)

urlpatterns = [
    url(r'^$', case.IndexView.as_view(), name='index'),

    url(r'^check/execs$', check.execution, name='check_execution'),
    url(r'^check/$', check.manager, name='check_manager'),
    url(r'^check/del/$', check.delete, name='check_delete'),
    url(r'^check/edit/$', check.edit, name='check_edit'),
    url(r'^check/save/$', check.save, name='check_save'),
    url(r'^check/execution/(?P<pk>[0-9]+)/$', check.executions, name='check_execution'),

    url(r'^alarm_info/$', alert.AlertView.as_view(), name='alarm_info'),

    url(r'^case/execs$', case.execution, name='case_execution'),
    # url(r'^case/$', case.manager, name='case_manager'),
    url(r'^case/$', case.CaseView.as_view(), name='case_manager'),
    url(r'^case/edit/$', case.edit, name='case_edit'),
    url(r'^case/save/$', case.save, name='case_save'),
    url(r'^case/del/$', case.delete, name='case_delete'),
    url(r'^case/runtest/(?P<pk>[0-9]+)/$', case.runtest, name='case_runtest'),


    url(r'^test/$', case.test, name='test'),
    url(r'^case/(?P<pk>[0-9]+)/$', case.todo, name='edit'),
    url(r'^case/invalid/$', case.todo, name='invalid'),
    url(r'^case/add/$', case.add, name='add'),
    url(r'^case/status/(?P<status>[0-9]+)/$', case.todo, name='status'),

    url(r'^case/exec/(?P<etlid>[0-9]+)/$', case.todo, name='exec'),
    url(r'^case/execlog/(?P<execid>[0-9]+)/$', case.todo, name='execlog'),
    url(r'^case/getexeclog/(?P<execid>[0-9]+)/$', case.todo, name='getexeclog'),
    url(r'^case/exec_list/(?P<jobid>[0-9]+)/$', case.todo, name='exec_list'),


    url(r'^sche/$', case.todo, name='sche_list'),
    url(r'^sche/add/$', case.todo, name='sche_add'),


    url(r'^rest/', include(router.urls)),
]