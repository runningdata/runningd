from django.conf.urls import url

from metamap.views import metas

app_name = 'meta'
urlpatterns = [
    url(r'^list/$', metas.MetaListView.as_view(), name='meta_list'),
    url(r'^add/$', metas.add, name='add_meta'),
    url(r'^(?P<pk>[0-9]+)/$', metas.edit, name='edit_meta'),
    url(r'^col_search/$', metas.ColView.as_view(), name='col_list'),
    url(r'^tbl_search/$', metas.TBLView.as_view(), name='tbl_list'),
    url(r'^tbl_search/(?P<tblid>[0-9]+)/$', metas.get_table, name='tbl_info'),
]
