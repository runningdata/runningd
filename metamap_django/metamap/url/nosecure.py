from django.conf.urls import url

from metamap.views import deps
from metamap.views import ops

app_name = 'nosecure'
urlpatterns = [
    url(r'^ops/push_single_msg/$', ops.push_single_msg, name='push_single_msg'),
    url(r'^ops/push_single_email/$', ops.push_single_email, name='push_single_email'),
    url(r'^generate_job_dag_v2/(?P<schedule>[0-9])/(?P<group_name>\w+)/$', deps.generate_job_dag_v2,
        name='generate_job_dag_v2'),
]
