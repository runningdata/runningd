from django.conf.urls import url

from will_common.views import common

app_name = 'common'

urlpatterns = [

    url(r'^user/$', common.modify_pwd, name='modify_pwd'),


]