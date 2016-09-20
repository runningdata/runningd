# !/usr/bin/env python
# -*- coding:utf-8 -*-
from django.db import models
import datetime
from django.utils import timezone

from metamap.djcelery_models import DjceleryCrontabschedule, DjceleryIntervalschedule



class AnaETL(models.Model):
    name = models.CharField(max_length=20)
    headers = models.TextField(null=False, blank=False)
    query = models.TextField()
    author = models.CharField(max_length=20, blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now)
    utime = models.DateTimeField(null=True)
    priority = models.IntegerField(default=5, blank=True)
    variables = models.CharField(max_length=2000, default='')
    valid = models.IntegerField(default=1)
    auth_users = models.TextField(default='',null=False, blank=False)

    __str__ = query

    def is_auth(self, user):
        if len(self.auth_users) == 0 :
            return True
        else:
            split = self.auth_users.split(',')
            if user in split:
                return True
        return False

    def __str__(self):
        return self.name

class ETL(models.Model):
    query = models.TextField()
    meta = models.CharField(max_length=20)
    tblName = models.CharField(max_length=100, db_column='tbl_name')
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.TextField(db_column='pre_sql', blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now)
    priority = models.IntegerField(default=5, blank=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    valid = models.IntegerField(default=1)
    setting = models.CharField(max_length=200, default='')
    variables = models.CharField(max_length=2000, default='')

    __str__ = query

    def __str__(self):
        return self.query

    def was_published_recently(self):
        return self.ctime >= timezone.now - datetime.timedelta(days=1)


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
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
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


class WillDependencyTask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    schedule = models.IntegerField(null=False, default=1)  # 0 天 1 周 2 月 3 季度 4 cron
    valid = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    utime = models.DateTimeField(null=True)
    variables = models.TextField()
    desc = models.TextField()
    rel_id = models.IntegerField(null=True, blank=False, help_text="ETL or Email id")
    type = models.IntegerField(default=1, blank=False, null=False, help_text="1 ETL; 2 EMAIL;")

    class Meta:
        unique_together = (('rel_id', 'schedule', 'type'),)

    def get_schedule(self):
        task = PeriodicTask.objects.get(willtask_id=self.id)
        if self.schedule == 4:
            cron = task.crontab
            return cron.minute + ' ' + cron.hour + ' ' + cron.day_of_month + ' ' + cron.month_of_year + ' ' + cron.day_of_week
        else:
            return ''


class PeriodicTask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField(default='[]')
    kwargs = models.TextField(default='{}')
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.IntegerField(default=1)
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField(default=0)
    date_changed = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    crontab = models.ForeignKey(DjceleryCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjceleryIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    willtask = models.ForeignKey(WillDependencyTask, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'djcelery_periodictask'
        managed = False

class BIUser(models.Model):
    username = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        db_table = 'sys_users'
        managed = False

class Exports(models.Model):
    '''
    定时任务执行记录
    '''
    file_loc = models.CharField(max_length=120, db_column='file_loc')
    task = models.ForeignKey(WillDependencyTask, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    command = models.TextField()

    def __str__(self):
        return self.file_loc