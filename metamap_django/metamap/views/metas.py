from metamap.db_views import ColMeta, TBL
from metamap.models import TblBlood, ETL
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.utils import timezone
import datetime
from django.db import connections

from metamap.utils.constants import DEFAULT_PAGE_SIEZE


class MetaView(generic.ListView):
    template_name = 'meta/list.html'
    context_object_name = 'metas'

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ColMeta.objects.using('hivemeta').filter(col_name__contains=tbl_name_).order_by('db_id')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ColMeta.objects.using('hivemeta').all()

    def get_context_data(self, **kwargs):
        context = super(MetaView, self).get_context_data(**kwargs)
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
    return render(request, 'meta/table_info.html', {'result': tbl})

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
