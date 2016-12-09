# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.db import models

from will_common.utils.fileds import Long2Date


class DB(models.Model):
    db_id = models.BigIntegerField(max_length=20, primary_key=True)
    desc = models.CharField(max_length=4000)
    db_location_uri = models.CharField(max_length=4000)
    name = models.CharField(max_length=128)
    owner_name = models.CharField(max_length=128)
    owner_type = models.CharField(max_length=10)
    class Meta:
        managed = False
        db_table = 'DBS'

class TBL(models.Model):
    db = models.ForeignKey(DB, on_delete=models.DO_NOTHING)
    tbl_id = models.BigIntegerField(max_length=20, primary_key=True)
    create_time = Long2Date()
    owner = models.CharField(max_length=767)
    tbl_name = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'TBLS'

class ColMeta(models.Model):
    '''
       字段对应meta
    '''
    id = models.IntegerField(primary_key=True)
    db = models.ForeignKey(DB, on_delete=models.DO_NOTHING)
    location = models.CharField(max_length=300, null=True)
    tbl = models.ForeignKey(TBL, on_delete=models.DO_NOTHING)
    tbl_type = models.CharField(max_length=30, null=True)
    col_type_name = models.CharField(max_length=300, null=True)
    col_comment = models.CharField(max_length=300, null=True)
    col_name = models.CharField(max_length=300, null=True)

    class Meta:
        managed = False
        db_table = 'col_tbl_db_view'