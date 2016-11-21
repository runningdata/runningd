from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
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
    # url(r'^$', login_required(case.IndexView.as_view()), name='index'),

    url(r'^$', case.IndexView.as_view(), name='index'),
    url(r'^check/execs$', login_required(check.execution), name='check_execution'),
    url(r'^check/$', login_required(check.manager), name='check_manager'),
    url(r'^check/del/$', login_required(check.delete), name='check_delete'),
    url(r'^check/edit/$', login_required(check.edit), name='check_edit'),
    url(r'^check/save/$', login_required(check.save), name='check_save'),
    url(r'^check/execution/(?P<pk>[0-9]+)/$', login_required(check.executions), name='check_execution'),

    url(r'^alarm_info/$', login_required(alert.AlertView.as_view()), name='alarm_info'),

    url(r'^case/execs$', login_required(case.execution), name='case_execution'),
    # url(r'^case/$', case.manager, name='case_manager'),
    url(r'^case/$', login_required(case.CaseView.as_view()), name='case_manager'),
    url(r'^case/edit/$', login_required(case.edit), name='case_edit'),
    url(r'^case/save/$', login_required(case.save), name='case_save'),
    url(r'^case/del/$', login_required(case.delete), name='case_delete'),
    url(r'^case/runtest/(?P<pk>[0-9]+)/$', login_required(case.runtest), name='case_runtest'),


    url(r'^test/$', login_required(case.test), name='test'),



    url(r'^rest/', include(router.urls)),
]