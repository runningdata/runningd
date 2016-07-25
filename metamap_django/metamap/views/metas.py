from metamap.models import TblBlood,ETL
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.utils import timezone
import datetime

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'latest_etl_list'

    def get_queryset(self):
        return ETL.objects.order_by('id')[:5]

class EditView(generic.DetailView):
    template_name = 'etl/edit.html'
    context_object_name = 'etl'

    def get_object(self):
        return ETL.objects.get(pk=1)

