# !/usr/bin/env python
# -*- coding:utf-8 -*-
from django.db import models
import datetime
from django.utils import timezone

from metamap.djcelery_models import DjceleryCrontabschedule, DjceleryIntervalschedule


class ETL(models.Model):
    query = models.TextField()
    meta = models.CharField(max_length=20)
    tblName = models.CharField(max_length=100, db_column='tbl_name')
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.TextField(db_column='pre_sql', blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now())
    priority = models.IntegerField(default=5, blank=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    valid = models.IntegerField(default=1)
    setting = models.CharField(max_length=200, default='')
    variables = models.CharField(max_length=2000, default='')

    __str__ = query

    def __str__(self):
        return self.query

    def test_add(self, a, b):
        return a + b;

    def was_published_recently(self):
        return self.ctime >= timezone.now() - datetime.timedelta(days=1)


class TblBlood(models.Model):
    class Meta:
        unique_together = (('tblName', 'parentTbl', 'valid'),)

    tblName = models.CharField(max_length=100, db_column='tbl_name')
    parentTbl = models.CharField(max_length=30, db_column='parent_tbl')
    relatedEtlId = models.IntegerField(db_column='related_etl_id')
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)

    def __str__(self):
        return self.parentTbl + '-->' + self.tblName


class Executions(models.Model):
    '''
    任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    # jobId = models.IntegerField(db_column='job_id')
    job = models.ForeignKey(ETL, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)

    def __str__(self):
        return self.logLocation


class Meta(models.Model):
    '''
       数据库对应meta
    '''
    meta = models.CharField(max_length=30, unique=True)
    db = models.CharField(max_length=30)
    settings = models.CharField(max_length=300, null=True)
    type = valid = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)

    def __str__(self):
        return self.meta



class PeriodicTask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.IntegerField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjceleryCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjceleryIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    etl = models.ForeignKey(ETL, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'djcelery_periodictask'