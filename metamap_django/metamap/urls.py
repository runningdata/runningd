from django.conf.urls import url, include
from rest_framework import routers

from metamap.views import sche_etl, export
from metamap.views import sqoop
from metamap.views.export import AnaETLViewSet
from metamap.views.etls import ETLViewSet, SqoopHive2MysqlViewSet
from metamap.views.sche_ana import ExportsViewSet, BIUserViewSet
from metamap.views.sqoop import SqoopHiveMetaViewSet, SqoopMysqlMetaViewSet
from views import etls, metas

app_name = 'metamap'

router = routers.DefaultRouter()
router.register(r'etls', ETLViewSet)
router.register(r'hive2mysql', SqoopHive2MysqlViewSet)
router.register(r'users', BIUserViewSet)
router.register(r'emails', AnaETLViewSet)
router.register(r'exports', ExportsViewSet)
router.register(r'sqoop_hive_meta', SqoopHiveMetaViewSet)
router.register(r'sqoop_mysql_meta', SqoopMysqlMetaViewSet)

urlpatterns = [

    url(r'^$', etls.IndexView.as_view(), name='index'),

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

    url(r'^etls/generate_job_dag/(?P<schedule>[0-9])/$', etls.generate_job_dag, name='generate_job_dag'),


    url(r'^meta/list/$', metas.MetaListView.as_view(), name='meta_list'),
    url(r'^meta/add/$', metas.add, name='add_meta'),
    url(r'^meta/(?P<pk>[0-9]+)/$', metas.edit, name='edit_meta'),
    url(r'^meta/col_search/$', metas.ColView.as_view(), name='col_list'),
    url(r'^meta/tbl_search/$', metas.TBLView.as_view(), name='tbl_list'),
    url(r'^meta/tbl_search/(?P<tblid>[0-9]+)/$', metas.get_table, name='tbl_info'),

    url(r'^sqoop/$', sqoop.Hive2MysqlListView.as_view(), name='h2m_sqoop_list'),
    url(r'^sqoop/(?P<pk>[0-9]+)/$', sqoop.edit, name='h2m_sqoop_edit'),
    url(r'^sqoop/add/$', sqoop.add, name='h2m_sqoop_add'),
    url(r'^sqoop/review/(?P<sqoop_id>[0-9]+)/$', sqoop.review, name='h2m_ssqoop_review'),

    url(r'^sqoop/exec/(?P<sqoopid>[0-9]+)/$', sqoop.exec_job, name='sqoop_exec'),
    url(r'^sqoop/execlog/(?P<execid>[0-9]+)/$', sqoop.exec_log, name='sqoop_execlog'),
    url(r'^sqoop/getexeclog/(?P<execid>[0-9]+)/$', sqoop.get_exec_log, name='sqoop_getexeclog'),
    url(r'^sqoop/status/(?P<status>[0-9]+)/$', sqoop.StatusJobView.as_view(), name='status'),

    url(r'^tasks/tasks/$', sche_etl.get_all_tasks, name='tasks'),
    url(r'^tasks/update/$', sche_etl.update_tasks_interval, name='update_tasks_interval'),

    url(r'^sche/$', sche_etl.ScheDepListView.as_view(), name='sche_list'),
    url(r'^sche/(?P<pk>[0-9]+)/$', sche_etl.edit, name='sche_edit'),
    url(r'^sche/etl/(?P<etlid>[0-9]+)/$', sche_etl.sche_etl_list, name='sche_etl_list'),
    url(r'^schecron/$', sche_etl.sche_cron_list, name='sche_cron_list'),
    url(r'^sche/add/$', sche_etl.add, name='sche_add'),
    url(r'^sche/migrate/$', sche_etl.migrate_jobs, name='migrate'),


    url(r'^rest/', include(router.urls)),
    url(r'^json/', etls.get_json),
]