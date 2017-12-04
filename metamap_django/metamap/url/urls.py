from django.conf.urls import url, include
from rest_framework import routers

from metamap.models import JarAppExecutions, SqoopMysql2HiveExecutions, Executions, SqoopHive2MysqlExecutions, \
    ExecutionsV2
from metamap.views import deps
from metamap.views import export
from metamap.views import jar
from metamap.views import ops
from metamap.views import sche_etl
from metamap.views import sche_etl_v2
from metamap.views import sche_multi
from metamap.views import source
from metamap.views import sqoop
from metamap.views import sqoop2
from metamap.rest.rest_views import ETLViewSet, SqoopHive2MysqlViewSet, SqoopMysql2HiveViewSet, SourceAppViewSet, \
    JarAppViewSet, AnaETLViewSet, SqoopHiveMetaViewSet, SqoopMysqlMetaViewSet, ExecObjViewSet
from metamap.views import to2cleaner
from metamap.views import usermanager
from metamap.views.sche_ana import ExportsViewSet
from metamap.views import etls, metas
from metamap.views import common

app_name = 'metamap'

router = routers.DefaultRouter()
router.register(r'etls', ETLViewSet)
router.register(r'hive2mysql', SqoopHive2MysqlViewSet)
router.register(r'mysql2hive', SqoopMysql2HiveViewSet)
router.register(r'sourceapp', SourceAppViewSet)
router.register(r'jarapp', JarAppViewSet)
router.register(r'exports', ExportsViewSet)
router.register(r'execobjs', ExecObjViewSet)
router.register(r'sqoop_hive_meta', SqoopHiveMetaViewSet)
router.register(r'sqoop_mysql_meta', SqoopMysqlMetaViewSet)

urlpatterns = [

    url(r'^$', etls.IndexView.as_view(), name='index'),
    url(r'^ops/task_queue/$', ops.task_queue, name='task_queue'),
    url(r'^ops/dfs_usage_his/$', ops.dfs_usage_his, name='dfs_usage_his'),
    url(r'^ops/dfs_usage/$', ops.dfs_usage, name='dfs_usage'),
    url(r'^ops/push_msg/$', ops.push_msg, name='push_msg'),
    url(r'^ops/hdfs_files/$', ops.hdfs_files, name='hdfs_files'),
    url(r'^ops/hdfs_del/(?P<filename>.*)/$', ops.hdfs_del, name='hdfs_del'),
    url(r'^ops/up_hdfs/$', ops.upload_hdfs_file, name='up_hdfs'),
    url(r'^ops/up_hdfs/$', ops.upload_hdfs_file, name='up_hdfs'),
    # url(r'^users/add/$', usermanager.add_user, name='add_user'),
    # url(r'^users/$', usermanager.list_user, name='list_user'),

    url(r'hdfs/tail', ops.tail_hdfs, name='tail_hdfs'),
    url(r'hdfs/check_file', ops.check_file, name='check_file'),
    url(r'nginx_auth_test', etls.nginx_auth_test, name='nginx_auth_test'),
    url(r'^etls/(?P<pk>[0-9]+)/$', etls.edit, name='edit'),
    url(r'^etls/invalid/$', etls.InvalidView.as_view(), name='invalid'),
    url(r'^etls/add/$', etls.add, name='add'),
    url(r'^etls/status/(?P<status>[0-9]+)/$',
        common.StatusListView.as_view(url_base='etls', model=Executions), name='status'),
    url(r'^etls/his/(?P<tblName>.*)/$', etls.his, name='his'),
    url(r'^etls/blood/$', etls.blood_by_name, name='blood_by_name'),
    url(r'^etls/preview_dag/$', etls.preview_job_dag, name='preview_job_dag'),
    url(r'^etls/blood/(?P<etlid>[0-9]+)/$', etls.blood_dag, name='blood'),
    url(r'^etls/restart_job/', etls.restart_job, name='restart_job'),
    url(r'^etls/check_dag/(?P<etlid>[0-9]+)/$', etls.check_dag, name='check_dag'),

    url(r'^etls/review_sql/(?P<etlid>[0-9]+)/$', etls.review_sql, name='review_sql'),
    url(r'^etls/exec/(?P<etlid>[0-9]+)/$', etls.exec_job, name='exec'),
    url(r'^etls/execlog/(?P<execid>[0-9]+)/$', etls.exec_log, name='execlog'),
    url(r'^etls/getexeclog/(?P<execid>[0-9]+)/$', etls.get_exec_log, name='getexeclog'),
    url(r'^etls/exec_list/(?P<jobid>[0-9]+)/$', etls.ExecLogView.as_view(), name='exec_list'),

    url(r'^etls/generate_job_dag/(?P<schedule>[0-9])/(?P<group_name>\w+)/$', etls.generate_job_dag, name='generate_job_dag'),
    url(r'^h2m/generate_job_dag/(?P<schedule>[0-9])/(?P<group_name>\w+)/$', sqoop.generate_job_dag, name='generate_sqoop_job_dag'),
    url(r'^m2h/generate_job_dag/(?P<schedule>[0-9])/(?P<group_name>\w+)/$', sqoop2.generate_job_dag, name='generate_sqoop2_job_dag'),

    url(r'^h2m/$', sqoop.Hive2MysqlListView.as_view(), name='h2m_sqoop_list'),
    url(r'^h2m/(?P<pk>[0-9]+)/$', sqoop.edit, name='h2m_sqoop_edit'),
    url(r'^h2m/add/$', sqoop.add, name='h2m_sqoop_add'),
    url(r'^h2m/review/(?P<sqoop_id>[0-9]+)/$', sqoop.review, name='h2m_ssqoop_review'),
    url(r'^h2m/restart_job/', sqoop.restart_job, name='h2m_restart_job'),

    url(r'^h2m/exec/(?P<sqoopid>[0-9]+)/$', sqoop.exec_job, name='sqoop_exec'),
    url(r'^h2m/execlog/(?P<execid>[0-9]+)/$', sqoop.exec_log, name='sqoop_execlog'),
    url(r'^h2m/getexeclog/(?P<execid>[0-9]+)/$', sqoop.get_exec_log, name='sqoop_getexeclog'),
    url(r'^h2m/status/(?P<status>[0-9]+)/$',
        common.StatusListView.as_view(url_base='h2m', model=SqoopHive2MysqlExecutions), name='sqoop_status'),

    url(r'^executions/status/(?P<status>[0-9]+)/$',
        common.StatusListView.as_view(url_base='executions', model=ExecutionsV2), name='executions_status'),
    url(r'^executions/execlog/(?P<execid>[0-9]+)/$', ops.exec_log, name='executions_execlog'),
    url(r'^executions/getexeclog/(?P<execid>[0-9]+)/$', ops.get_exec_log, name='executions_getexeclog'),


    url(r'^m2h/$', sqoop2.Mysql2HiveListView.as_view(), name='h2m_sqoop2_list'),
    url(r'^m2h/(?P<pk>[0-9]+)/$', sqoop2.edit, name='h2m_sqoop2_edit'),
    url(r'^m2h/add/$', sqoop2.add, name='h2m_sqoop2_add'),
    url(r'^m2h/review/(?P<sqoop_id>[0-9]+)/$', sqoop2.review, name='h2m_sqoop2_review'),
    url(r'^m2h/exec/(?P<sqoopid>[0-9]+)/$', sqoop2.exec_job, name='sqoop2_exec'),
    url(r'^m2h/execlog/(?P<execid>[0-9]+)/$', sqoop2.exec_log, name='sqoop2_execlog'),
    url(r'^m2h/getexeclog/(?P<execid>[0-9]+)/$', sqoop2.get_exec_log, name='sqoop2_getexeclog'),
    url(r'^m2h/status/(?P<status>[0-9]+)/$',
        common.StatusListView.as_view(url_base='m2h', model=SqoopMysql2HiveExecutions), name='sqoop2_status'),

    url(r'^tasks/tasks/$', sche_etl_v2.get_all_tasks, name='tasks'),
    url(r'^tasks/update/$', sche_etl_v2.update_tasks_interval, name='update_tasks_interval'),

    url(r'^sche/$', sche_etl_v2.ScheDepListView.as_view(), name='sche_list'),
    url(r'^sche/(?P<pk>[0-9]+)/$', sche_etl_v2.edit, name='sche_edit'),
    url(r'^sche/etl/(?P<etlid>[0-9]+)/$', sche_etl_v2.sche_etl_list, name='sche_etl_list'),
    url(r'^schecron/$', sche_etl_v2.sche_cron_list, name='sche_cron_list'),
    url(r'^sche/add/$', sche_etl_v2.add, name='sche_add'),
    url(r'^sche/migrate/$', sche_etl_v2.migrate_jobs, name='migrate'),

    url(r'^sche_multi/add/$', sche_multi.add, name='add_multi'),
    url(r'^sche_multi/(?P<pk>[0-9]+)/$', sche_multi.edit, name='sche_multi_edit'),
    url(r'^sche_multi/$', sche_multi.ScheMultiListView.as_view(), name='sche_multi_list'),

    url(r'^source/$', source.IndexView.as_view(), name='source_index'),
    url(r'^source/add/$', source.add, name='source_add'),
    url(r'^source/(?P<pk>[0-9]+)/$', source.edit, name='source_edit'),
    url(r'^source/review/(?P<pk>[0-9]+)/$', source.review, name='source_review'),
    url(r'^source/exec/(?P<pk>[0-9]+)/$', source.exec_job, name='source_exec'),

    url(r'^jar/$', jar.IndexView.as_view(), name='jar_index'),
    url(r'^jar/add/$', jar.add, name='jar_add'),
    url(r'^jar/del/(?P<pk>[0-9]+)/$', jar.delete, name='jar_delete'),
    url(r'^jar/(?P<pk>[0-9]+)/$', jar.edit, name='jar_edit'),
    url(r'^jar/review/(?P<pk>[0-9]+)/$', jar.review, name='jar_review'),
    url(r'^jar/exec/(?P<pk>[0-9]+)/$', jar.exec_job, name='jar_exec'),
    url(r'^jar/execlog/(?P<execid>[0-9]+)/$', jar.exec_log, name='jar_execlog'),
    url(r'^jar/getexeclog/(?P<execid>[0-9]+)/$', jar.get_exec_log, name='jar_getexeclog'),
    url(r'^jar/status/(?P<status>[0-9]+)/$', common.StatusListView.as_view(url_base='jar', model=JarAppExecutions),
        name='jar_status'),

    url(r'^deps/deps/(?P<pk>[0-9]+)/$', deps.edit_deps, name='jar_deps'),
    url(r'^deps/generate_job_dag_v2/(?P<schedule>[0-9])/(?P<group_name>\w+)/$', deps.generate_job_dag_v2, name='generate_job_dag_v2'),

    url(r'^source/get_engine_type/$', source.get_engine_type, name='get_engine_type'),
    url(r'^rest/', include(router.urls)),
    url(r'^json/', etls.get_json),
]
