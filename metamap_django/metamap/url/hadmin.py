from django.conf.urls import url
from metamap.views import hadmin

app_name = 'hadmin'

urlpatterns = [
    url(r'^add/$', hadmin.add, name='hadmin_add'),

]
