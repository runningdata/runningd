from django.conf.urls import url
from metamap.views import hadmin
from metamap.views import ops

app_name = 'hooks'

urlpatterns = [
    url(r'^alert/$', ops.alert_for_prome, name='alert')
]
