from django.conf.urls import url

from dqms import views

app_name = 'dqms'


urlpatterns = [
    url(r'^$', views.index, name='index'),
]