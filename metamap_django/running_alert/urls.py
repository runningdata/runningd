from django.conf.urls import url, include
from rest_framework import routers

from running_alert.views import index, spark

app_name = 'alert'

router = routers.DefaultRouter()

urlpatterns = [

    url(r'^$', index.IndexView.as_view(), name='index'),
    url(r'^add/$', index.add, name='add'),
    url(r'^(?P<pk>[0-9]+)/$', index.edit, name='edit'),
    url(r'^spark/(?P<pk>[0-9]+)/$', spark.edit, name='spark_edit'),
    url(r'^spark/add/$', spark.add, name='spark_add'),
    url(r'^spark/$', spark.IndexView.as_view(), name='spark_index'),

    url(r'^rest/', include(router.urls)),

]
