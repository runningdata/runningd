from django.conf.urls import url
from metamap.views import hadmin
from metamap.views import ops

app_name = 'hadmin'

urlpatterns = [
    url(r'^add/$', hadmin.add, name='hadmin_add'),
    url(r'^ops/rerun/$', ops.rerun, name='rerun'),
    url(r'^jobs/finished/$', ops.exec_history, name='exec_history'),
    url(r'^jobs/finished_page/$', ops.exec_history_page, name='exec_history_page'),
]
