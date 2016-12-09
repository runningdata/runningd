# !/usr/bin/env python
# -*- coding:utf-8 -*-
from django.db import models
import datetime
from django.utils import timezone

from will_common.djcelery_models import DjceleryCrontabschedule, DjceleryIntervalschedule
from will_common.models import PeriodicTask, WillDependencyTask
import will_common
from will_common.templatetags.etlutils import sche_type_dic


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
    auth_users = models.TextField(default='', null=False, blank=False)

    __str__ = query

    def is_auth(self, user):
        if len(self.auth_users) == 0:
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
    tblName = models.CharField(max_length=100, db_column='tbl_name', verbose_name=u"ETL名称")
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.TextField(db_column='pre_sql', blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now)
    priority = models.IntegerField(default=5, blank=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    valid = models.IntegerField(default=1, verbose_name=u"是否生效")
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


class BIUser(models.Model):
    username = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'sys_users'
        managed = False


class SqoopMysql2Hive(models.Model):
    mysql_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_m')
    hive_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_h')
    columns = models.TextField(null=True)
    query = models.TextField(null=True)
    mysql_tbl = models.CharField(max_length=300, null=False)
    option = models.TextField(null=True, )


#
# class WillDependencyTask(models.Model):
#     name = models.CharField(unique=True, max_length=200)
#     schedule = models.IntegerField(null=False, default=1)  # 0 天 1 周 2 月 3 季度 4 cron
#     valid = models.IntegerField(default=1)
#     ctime = models.DateTimeField(default=timezone.now)
#     utime = models.DateTimeField(null=True)
#     variables = models.TextField()
#     desc = models.TextField()
#     rel_id = models.IntegerField(null=True, blank=False, help_text="ETL or Email id")
#     type = models.IntegerField(default=1, blank=False, null=False, help_text="1 ETL; 2 EMAIL; 3 Hive2Mysql; 4 Mysql2Hive")
#
#     class Meta:
#         db_table = 'metamap_willdependencytask'
#         unique_together = (('rel_id', 'schedule', 'type'),)
#         managed = False

class SqoopHive2Mysql(models.Model):
    name = models.CharField(max_length=40, null=False, default='none')
    mysql_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='h2m_m')
    hive_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='h2m_h')
    columns = models.TextField(null=True)
    update_key = models.TextField(null=True)
    update_mode = models.CharField(max_length=30, default='allowinsert')
    hive_tbl = models.CharField(max_length=300, null=False, default='none')
    mysql_tbl = models.CharField(max_length=300, null=False)
    option = models.TextField(null=True, )
    settings = models.TextField(null=True)
    partion_expr = models.TextField(null=True)
    parallel = models.IntegerField(default=1, verbose_name='并发执行')
    ctime = models.DateTimeField(default=timezone.now)


class Exports(models.Model):
    '''
    定时任务执行记录
    '''
    file_loc = models.CharField(max_length=120, db_column='file_loc')
    task = models.ForeignKey(WillDependencyTask, on_delete=models.DO_NOTHING, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    command = models.TextField()

    # class Meta:
    #     managed = False

    def __str__(self):
        return self.file_loc


class Executions(models.Model):
    '''
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    job = models.ForeignKey(ETL, on_delete=models.CASCADE, null=False)
    # job = models.IntegerField(default=-1, null=False)
    # job_name = models.CharField(max_length=120, null=False, default='noname')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)
    # type = models.IntegerField(default=-1, null=False, verbose_name="1 ETL; 2 EMAIL; 3 Hive2Mysql; 4 Mysql2Hive",
    #                            choices=sche_type_dic.items())

    def __str__(self):
        return self.logLocation


class SqoopHive2MysqlExecutions(models.Model):
    '''
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    job = models.ForeignKey(SqoopHive2Mysql, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)

    def __str__(self):
        return self.logLocation
