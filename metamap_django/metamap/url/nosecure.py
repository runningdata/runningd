from django.conf.urls import url

from metamap.views import ops

app_name = 'nosecure'
urlpatterns = [
    url(r'^ops/push_single_msg/$', ops.push_single_msg, name='push_single_msg'),
    url(r'^ops/push_single_email/$', ops.push_single_email, name='push_single_email'),
]
