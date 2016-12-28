from django.conf.urls import url, include

from rest_framework import routers
from will_common.views import common
from will_common.views.common import GroupsViewSet

app_name = 'common'

router = routers.DefaultRouter()
router.register(r'groups', GroupsViewSet)

urlpatterns = [
    url(r'^user/$', common.modify_pwd, name='modify_pwd'),
    url(r'^rest/', include(router.urls)),
]