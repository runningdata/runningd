from django.conf.urls import url

from running_alert.views import hooks

app_name = 'hooks'

urlpatterns = [
    url(r'^alert/$', hooks.alert_for_prome, name='alert')
]
