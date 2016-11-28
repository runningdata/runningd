# !/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone

from will_common.djcelery_models import DjceleryCrontabschedule
from will_common.djcelery_models import DjceleryIntervalschedule

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone = models.BigIntegerField(default=110)


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
        db_table = 'metamap_willdependencytask'
        unique_together = (('rel_id', 'schedule', 'type'),)
        managed = False

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