import logging

from django.core.exceptions import ObjectDoesNotExist

from metamap.db_views import ColMeta, TBL
from metamap.models import ETL, Meta
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic

from will_common.utils import httputils
from will_common.utils import userutils
from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from will_common.views.common import GroupListView

logger = logging.getLogger('info')

class MetaListView(GroupListView):
    template_name = 'meta/meta_list.html'
    context_object_name = 'metas'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            search = self.request.GET['search']
            return Meta.objects.filter(meta__contains=search).order_by('ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return Meta.objects.all()

    def get_context_data(self, **kwargs):
        context = super(MetaListView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context

def add(request):
    if request.method == 'POST':
        meta = Meta()
        httputils.post2obj(meta, request.POST, 'id')
        userutils.add_current_creator(meta, request)
        meta.save()
        logger.info('Meta has been created successfully : %s ' % meta)
        return HttpResponseRedirect(reverse('meta:meta_list'))
    else:
        return render(request, 'meta/edit.html')

def edit(request, pk):
    if request.method == 'POST':
        meta = Meta.objects.filter(valid=1).get(pk=int(pk))
        httputils.post2obj(meta, request.POST, 'id')
        userutils.add_current_creator(meta, request)
        meta.save()
        logger.info('Meta has been created successfully : %s ' % meta)
        return HttpResponseRedirect(reverse('meta:meta_list'))
    else:
        obj = Meta.objects.get(pk=pk)
        return render(request, 'meta/edit.html', {'obj': obj})

class ColView(generic.ListView):
    template_name = 'meta/col_list.html'
    context_object_name = 'metas'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ColMeta.objects.using('hivemeta').filter(col_name__contains=tbl_name_).order_by('db_id')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ColMeta.objects.using('hivemeta').all()

    def get_context_data(self, **kwargs):
        context = super(ColView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context

        # cursor = connections['hivemeta'].cursor()
        # result = dict()
        # try:
        #     cursor.execute("  SELECT\n" +
        #                    "    db.DB_ID as db_id,\n" +
        #                    "    db.`NAME` as db_name,\n" +
        #                    "    a.TBL_ID as tbl_id,\n" +
        #                    "    a.TBL_NAME as tbl_name,\n" +
        #                    "    a.TBL_TYPE as tbl_type,\n" +
        #                    "    d.TYPE_NAME as col_type_name,\n" +
        #                    "    d.`COMMENT` as col_comment,\n" +
        #                    "    d.COLUMN_NAME as col_name\n" +
        #                    "FROM\n" +
        #                    "    TBLS a\n" +
        #                    "LEFT JOIN SDS b ON a.SD_ID = b.SD_ID\n" +
        #                    "LEFT JOIN COLUMNS_V2 d ON b.CD_ID = d.CD_ID\n" +
        #                    "LEFT JOIN DBS db ON a.DB_ID = db.DB_ID")
        #     result = dictfetchall(cursor=cursor)
        # finally:
        #     cursor.close()
        # return result


class TBLView(generic.ListView):
    template_name = 'meta/tbl_list.html'
    context_object_name = 'tbls'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return TBL.objects.using('hivemeta').filter(tbl_name__contains=tbl_name_).order_by('db_id')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return TBL.objects.using('hivemeta').all().order_by('db_id')

    def get_context_data(self, **kwargs):
        context = super(TBLView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def get_table(request, tblid):
    tbl = TBL.objects.using('hivemeta').get(pk=tblid)
    has_blood = True
    try:
        ETL.objects.get(valid=1, name=tbl.db.name + '@' + tbl.tbl_name)
    except ObjectDoesNotExist, e:
        has_blood = False
    return render(request, 'meta/table_info.html', {'result': tbl, 'has_blood': has_blood})

    # cursor = connections['hivemeta'].cursor()
    # result = dict()
    # whereStr = ' where 1=1 '
    # if request.GET['jobid']:
    #     whereStr += " and a.tbl_id = " + request.GET['jobid']
    # try:
    #     cursor.execute("select * from TBLS " + whereStr)
    #     result = dictfetchone(cursor=cursor)
    #     render(request, 'meta/table_info.html', {'tbl': result})
    # finally:
    #     cursor.close()
    # return result


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]


def dictfetchone(cursor):
    "Returns one row from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchone()
        ]
