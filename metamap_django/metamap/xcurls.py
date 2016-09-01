from django.conf.urls import url, include

from metamap.views import celery_view
from views import etls, metas

app_name = 'export'
from metamap.views.etls import router
urlpatterns = [
    url(r'^$', celery_view.export, name='export'),
    url(r'^execlog/(?P<loc>.+)/$', celery_view.execlog, name='execlog'),
    url(r'^(?P<filename>.+)/$', celery_view.getfile, name='getfile'),
]