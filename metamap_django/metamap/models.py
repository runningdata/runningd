from django.db import models
import datetime
from django.utils import timezone


class ETL(models.Model):
    query = models.CharField(max_length=2000)
    meta = models.CharField(max_length=20)
    tblName = models.CharField(max_length=30, db_column='tbl_name')
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.CharField(max_length=2000, db_column='pre_sql', blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now())
    priority = models.IntegerField(default=5, blank=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    valid = models.IntegerField(default=1)

    def __str__(self):
        return self.query

    def was_published_recently(self):
        return self.ctime >= timezone.now() - datetime.timedelta(days=1)


class TblBlood(models.Model):
    tblName = models.CharField(max_length=30, db_column='tbl_name')
    parentTbl = models.CharField(max_length=30, db_column='parent_tbl')
    relatedEtlId = models.IntegerField(db_column='related_etl_id')
    ctime = models.DateTimeField(default=timezone.now())
    valid = models.IntegerField(default=1)

    def __str__(self):
        return self.parentTbl + '-->' + self.tblName
