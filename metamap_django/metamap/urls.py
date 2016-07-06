from django.conf.urls import url

from . import views
app_name = 'metamap'
urlpatterns = [
   url(r'^$', views.IndexView.as_view(), name='index'),
   url(r'^etl/(?P<pk>[0-9]+)/$', views.EditView.as_view(), name='edit'),
]