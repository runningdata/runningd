from django.conf.urls import url
from metamap.views import to2cleaner

app_name = 'clean'

urlpatterns = [
    url(r'^clean_rel/$', to2cleaner.clean_rel_name, name='clean_rel'),
    url(r'^clean_m2h/$', to2cleaner.clean_M2H, name='clean_m2h'),
    url(r'^clean_h2m/$', to2cleaner.clean_H2M, name='clean_h2m'),
    url(r'^clean_etl/$', to2cleaner.clean_etl, name='clean_etl'),
    url(r'^clean_jar/$', to2cleaner.clean_JAR, name='clean_jar'),
    url(r'^clean_email/$', to2cleaner.clean_ANA, name='clean_email'),
    url(r'^clean_blood/$', to2cleaner.clean_blood, name='clean_blood'),
    url(r'^before_clean_blood/$', to2cleaner.clean_etlp_befor_blood, name='before_clean_blood'),
    url(r'^clean_task/$', to2cleaner.clean_deptask, name='clean_task'),
    url(r'^clean_ptask/$', to2cleaner.clean_period_tsk, name='clean_period_tsk'),
    url(r'^clean_null/$', to2cleaner.clean_null, name='clean_null'),
    url(r'^clean_exec_id/$', to2cleaner.clean_exec_obj_id, name='clean_exec_id'),
    url(r'^clean_group/$', to2cleaner.clean_group, name='clean_group'),
    url(r'^clean_exports/$', to2cleaner.clean_exports, name='clean_exports'),

]
