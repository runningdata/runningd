from django.conf.urls import url

from metamap.views import sche_etl, sche_ana, export

app_name = 'export'
urlpatterns = [
    url(r'^$', export.IndexView.as_view(), name='index'),
    url(r'^add/$', export.add, name='add'),

    url(r'^execlog/(?P<loc>.+)/$', sche_etl.execlog, name='execlog'),
    url(r'^sche/$', sche_ana.ScheDepListView.as_view(), name='sche_list'),
    url(r'^sche/(?P<pk>[0-9]+)/$', sche_ana.edit, name='sche_edit'),
    url(r'^sche/add/$', sche_ana.add, name='sche_add'),
    url(r'^(?P<filename>.+)/$', sche_etl.getfile, name='getfile'),
]
