# -*- coding: utf-8 -*
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from metamap.models import TblBlood, ETL
from metamap.utils import hivecli, httputils, dateutils
from metamap.utils.constants import *

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'

    def get_queryset(self):
        etls = ETL.objects.filter(valid=1)
        print etls
        return etls


class EditView(generic.DetailView):
    template_name = 'etl/edit.html'
    context_object_name = 'form'
    queryset = ETL.objects.all()


# class ETLForm(forms.ModelForm):
#     preSql = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control", "size": 10}))
#
#     class Meta:
#         model = ETL
#         exclude = ['id', 'ctime']


def find_parent_mermaid(blood, final_bloods, current=0):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)


def find_child_mermaid(blood, final_bloods, current=0):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)


def blood(request, etlid):
    blood = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1).get()
    final_bloods = set()
    final_bloods.add(clean_blood(blood, etlid))
    find_parent_mermaid(blood, final_bloods, etlid)
    find_child_mermaid(blood, final_bloods, etlid)
    return render(request, 'etl/blood.html', {'bloods': final_bloods})


def clean_blood(blood, current=0):
    '''
    为了方便mermaid显示，把blood里的@替换为__
    :param blood:
    :return:
    '''
    blood.parentTbl = blood.parentTbl.replace('@', '__')
    blood.tblName = blood.tblName.replace('@', '__')
    if current > 0:
        blood.tblName += ';style ' + blood.tblName.replace('@', '__') + ' fill:#f9f,stroke:#333,stroke-width:4px;'
    return blood


@transaction.atomic
def edit(request, pk):
    if request.method == 'POST':

        privious_etl = ETL.objects.filter(valid=1).get(pk=int(pk))
        privious_etl.valid = 0
        privious_etl.save()

        privious_etl.valid = 1
        privious_etl.id = None
        etl = privious_etl
        httputils.post2obj(etl, request.POST, 'id')

        etl.save()
        logger.info('ETL has been created successfully : %s ' % etl)
        deps = hivecli.getTbls(etl.query)
        for dep in deps:
            tblBlood = TblBlood(tblName=etl.tblName, parentTbl=dep, relatedEtlId=etl.id)
            tblBlood.save()
            logger.info('Tblblood has been created successfully : %s' % tblBlood)
        return HttpResponseRedirect(reverse('metamap:index2'))
    else:
        etl = ETL.objects.get(pk=pk)
        return render(request, 'etl/edit.html', {'etl': etl})


def exec_job(reques, etlid):
    etl = ETL.objects.get(id=etlid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-' + etl.tblName.replace('@', '__') + '.hql'

