from django.conf.urls import url, include
from rest_framework import routers

from metamap.rest.rest_views import AnaETLViewSet
from metamap.views import sche_etl, sche_ana, export

app_name = 'export'

router = routers.DefaultRouter()
router.register(r'emails', AnaETLViewSet)
urlpatterns = [
    url(r'^$', export.IndexView.as_view(), name='index'),
    url(r'^add/$', export.add, name='add'),
    url(r'^exec/(?P<pk>[0-9]+)/$', export.exec_job, name='exec'),
    url(r'^edit/(?P<pk>[0-9]+)/$', export.edit, name='edit'),
    url(r'^review_sql/(?P<pk>[0-9]+)/$', export.review_sql, name='review_sql'),
    url(r'^error_log/(?P<log>.*)/$', export.get_exec_log, name='error_log'),

    url(r'^execlog/(?P<loc>.+)/$', sche_etl.execlog, name='execlog'),
    url(r'^sche/$', sche_ana.ScheDepListView.as_view(), name='sche_list'),
    url(r'^sche/(?P<pk>[0-9]+)/$', sche_ana.edit, name='sche_edit'),
    url(r'^sche/add/$', sche_ana.add, name='sche_add'),
    url(r'^rest/', include(router.urls)),

    url(r'^(?P<filename>.+)/$', sche_etl.getfile, name='getfile'),
]
