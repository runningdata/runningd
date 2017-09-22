# !/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone

from will_common.djcelery_models import DjceleryCrontabschedule
from will_common.djcelery_models import DjceleryIntervalschedule


class OrgGroup(models.Model):
    name = models.CharField(max_length=200, verbose_name=u"组织名称")
    owners = models.CharField(max_length=100, verbose_name=u"负责人", blank=True, default='')
    hdfs_path = models.CharField(max_length=100, verbose_name=u"HDFS临时路径", blank=True, default='')

    # need_auth = models.IntegerField(default=1, verbose_name=u"是否需要验证", choices=(
    #     (1, '是'),
    #     (0, '否'),
    # ))
    # auth_uri = models.CharField(max_length=300, verbose_name=u"验证uri", blank=True, default='')
    def __str__(self):
        return self.name


class CommmonTimes(models.Model):
    ctime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    utime = models.DateTimeField(verbose_name=u'最近更新时间', default=timezone.now)

    class Meta:
        abstract = True


class CommmonCreators(models.Model):
    creator = models.ForeignKey('UserProfile', on_delete=models.DO_NOTHING, null=True, verbose_name=u'创建人')
    cgroup = models.ForeignKey('OrgGroup', on_delete=models.DO_NOTHING, null=True, verbose_name=u'所属组织')

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone = models.BigIntegerField(default=110)
    org_group = models.ForeignKey(OrgGroup, on_delete=models.DO_NOTHING, related_name='user_cgroup', null=True)

    def __str__(self):
        return self.user.username


class CeleryTask():
    def __init__(self, queue, command, name):
        self.queue = queue
        self.command = command
        self.name = name


class WillDependencyTask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    schedule = models.IntegerField(null=False, default=1)  # 0 天 1 周 2 月 3 季度 4 cron
    valid = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    utime = models.DateTimeField(null=True)
    variables = models.TextField()
    desc = models.TextField()
    rel_id = models.IntegerField(null=True, blank=False, help_text="ETL or Email id")
    type = models.IntegerField(default=100, blank=False, null=False,
                               help_text="1 ETL; 2 EMAIL; 3 Hive2Mysql; 4 Mysql2Hive; 5 jarfile")

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
    queue = models.CharField(max_length=200, blank=True, null=True, default='cron_tsk')
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
