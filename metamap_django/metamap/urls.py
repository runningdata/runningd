from django.conf.urls import url, include

from metamap.views import celery_view
from views import etls, metas

app_name = 'metamap'
from metamap.views.etls import router
urlpatterns = [

    url(r'^$', etls.IndexView.as_view(), name='index'),

    url(r'^xx/$', etls.xx, name='xx'),

    url(r'^etls/(?P<pk>[0-9]+)/$', etls.edit, name='edit'),
    url(r'^etls/invalid/$', etls.InvalidView.as_view(), name='invalid'),
    url(r'^etls/add/$', etls.add, name='add'),
    url(r'^etls/status/(?P<status>[0-9]+)/$', etls.StatusJobView.as_view(), name='status'),
    url(r'^etls/his/(?P<tblName>.*)/$', etls.his, name='his'),
    url(r'^etls/blood/$', etls.blood_by_name, name='blood_by_name'),
    url(r'^etls/preview_dag/$', etls.preview_job_dag, name='preview_job_dag'),
    url(r'^etls/blood/(?P<etlid>[0-9]+)/$', etls.blood_dag, name='blood'),

    url(r'^etls/review_sql/(?P<etlid>[0-9]+)/$', etls.review_sql, name='review_sql'),
    url(r'^etls/exec/(?P<etlid>[0-9]+)/$', etls.exec_job, name='exec'),
    url(r'^etls/execlog/(?P<execid>[0-9]+)/$', etls.exec_log, name='execlog'),
    url(r'^etls/getexeclog/(?P<execid>[0-9]+)/$', etls.get_exec_log, name='getexeclog'),
    url(r'^etls/exec_list/(?P<jobid>[0-9]+)/$', etls.ExecLogView.as_view(), name='exec_list'),

    url(r'^etls/generate_job_dag/$', etls.generate_job_dag, name='generate_job_dag'),


    url(r'^meta/list/$', metas.MetaListView.as_view(), name='meta_list'),
    url(r'^meta/add/$', metas.add, name='add_meta'),
    url(r'^meta/(?P<pk>[0-9]+)/$', metas.edit, name='edit_meta'),
    url(r'^meta/col_search/$', metas.ColView.as_view(), name='col_list'),
    url(r'^meta/tbl_search/$', metas.TBLView.as_view(), name='tbl_list'),
    url(r'^meta/tbl_search/(?P<tblid>[0-9]+)/$', metas.get_table, name='tbl_info'),

    url(r'^tasks/tasks/$', celery_view.get_all_tasks, name='tasks'),
    url(r'^tasks/update/$', celery_view.update_tasks_interval, name='update_tasks_interval'),

    url(r'^sche/$', celery_view.sche_list, name='sche_list'),
    url(r'^sche/add/$', celery_view.add, name='sche_add'),
    url(r'^sche/add/(?P<etlid>[0-9]+)/$', celery_view.add, name='sche_add_from_etl'),
    url(r'^sche/(?P<etlid>[0-9]+)/$', celery_view.sche_etl_list, name='sche_etl'),

    url(r'^rest/', include(router.urls)),
    url(r'^json/', etls.get_json),
]