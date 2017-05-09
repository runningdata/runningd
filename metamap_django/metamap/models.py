# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from django.contrib.auth.models import Group
from django.db import models
import datetime
from django.utils import timezone

from will_common.djcelery_models import DjceleryCrontabschedule, DjceleryIntervalschedule
from will_common.models import PeriodicTask, WillDependencyTask, UserProfile

logger = logging.getLogger('django')
from will_common.utils import hivecli


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
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='ana_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='ana_cgroup', null=True)

    __str__ = query

    def is_auth(self, user, group):
        if len(self.auth_users) == 0:
            return True
        else:
            split = self.auth_users.split(',')
            if user in split and self.cgroup.name == group:
                return True
        return False

    def __str__(self):
        return self.name


class SourceEngine(models.Model):
    name = models.CharField(max_length=20, verbose_name=u"引擎名称")
    bin_name = models.CharField(max_length=20, verbose_name=u"引擎启动脚本")
    enpath_path = models.CharField(max_length=300, verbose_name=u"引擎路径")

    def __str__(self):
        return self.name


class CompileTool(models.Model):
    name = models.CharField(max_length=20, verbose_name=u"引擎名称")
    bin_name = models.CharField(max_length=20, verbose_name=u"引擎启动脚本")
    opts = models.CharField(max_length=100, verbose_name=u"默认编译参数")
    target_path = models.CharField(max_length=100, verbose_name=u"默认目标文件路径")
    enpath_path = models.CharField(max_length=300, verbose_name=u"引擎路径")

    def __str__(self):
        return self.name


class SourceApp(models.Model):
    name = models.CharField(max_length=200, verbose_name=u"任务名称")
    engine_type = models.ForeignKey(SourceEngine, on_delete=models.DO_NOTHING,
                                    verbose_name=u"运行工具")
    git_url = models.CharField(max_length=200, verbose_name=u"git地址")
    branch = models.CharField(max_length=20, verbose_name=u"git分支")
    sub_dir = models.CharField(max_length=100, verbose_name=u"工作目录")
    main_func = models.CharField(max_length=100, verbose_name=u"入口类")
    compile_tool = models.ForeignKey(CompileTool, on_delete=models.DO_NOTHING,
                                     verbose_name=u"运行工具")
    priority = models.IntegerField(default=5, blank=True)
    valid = models.IntegerField(default=1, verbose_name=u"是否生效")
    engine_opts = models.TextField(default='', verbose_name=u"引擎运行参数", blank=True, null=True)
    main_func_opts = models.TextField(default='', verbose_name=u"入口类运行参数", blank=True, null=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='source_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='source_cgroup', null=True)
    ctime = models.DateTimeField(default=timezone.now)


class JarApp(models.Model):
    name = models.CharField(max_length=200, verbose_name=u"任务名称")
    engine_type = models.ForeignKey(SourceEngine, on_delete=models.DO_NOTHING,
                                    verbose_name=u"运行工具")
    main_func = models.CharField(max_length=100, verbose_name=u"入口类", blank=True, default='')
    priority = models.IntegerField(default=5, blank=True)
    jar_file = models.FileField(upload_to='jars', blank=True)
    valid = models.IntegerField(default=1, verbose_name=u"是否生效")
    engine_opts = models.TextField(default='', verbose_name=u"引擎运行参数", blank=True, null=True)
    main_func_opts = models.TextField(default='', verbose_name=u"入口类运行参数", blank=True, null=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='jar_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='jar_cgroup', null=True)
    ctime = models.DateTimeField(default=timezone.now)


class ETLObjRelated():
    '''
    every etl obj should extend me. for example: m2h, h2h, h2m .etc
    '''
    etl_type = 110

    def update_etlobj(self):
        self.clean_etlobj()
        obj, succeed = self.add_etlobj()
        obj.update_deps()
        return obj

    def add_etlobj(self):
        return ETLObj.objects.update_or_create(name=self.name, rel_id=self.id, type=self.etl_type)

    def clean_etlobj(self):
        obj = ETLObj.objects.get(rel_id=self.id, type=self.etl_type)
        if obj:
            obj.delete()

    def get_deps(self):
        '''
        这个是自动分析的依赖，不同于调度时获取的依赖，这是后者的前一个步骤，注意不要混淆了
        :return:
        '''
        return None


class ETL(models.Model, ETLObjRelated):
    etl_type = 1
    query = models.TextField()
    meta = models.CharField(max_length=20)
    name = models.CharField(max_length=100, db_column='tbl_name', verbose_name=u"ETL名称")
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.TextField(db_column='pre_sql', blank=True, null=True)
    ctime = models.DateTimeField(default=timezone.now)
    priority = models.IntegerField(default=5, blank=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    valid = models.IntegerField(default=1, verbose_name=u"是否生效")
    setting = models.CharField(max_length=200, default='')
    variables = models.CharField(max_length=2000, default='')
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='etl_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='etl_cgroup', null=True)

    __str__ = query

    def __str__(self):
        return self.query

    def get_deps(self):
        deps = hivecli.getTbls(self)

    def was_published_recently(self):
        return self.ctime >= timezone.now - datetime.timedelta(days=1)


class ETLObj(models.Model):
    name = models.CharField(max_length=100, db_column='name')
    type = models.IntegerField(default=1, blank=False, null=False,
                               help_text="1 ETL; 2 EMAIL; 3 Hive2Mysql; 4 Mysql2Hive; 5 sourcefile;6 jarfile")
    rel_id = models.IntegerField()

    def update_deps(self):
        '''
        better use this
        :param deps:
        :return:
        '''
        # TODO swith dict
        etl = ETL.objects.get(pk=self.rel_id)
        deps = etl.get_deps()
        dep_ids = [ETLObj.objects.get(name=dep).id for dep in deps]
        self.clean_deps(dep_ids)
        self.add_deps(dep_ids)
        logger.info('ETLBlood has been created successfully : %s' % deps)

    def add_deps(self, deps):
        for dep in deps:
            ETLBlood.objects.update_or_create(child_id=self.id, parent_id=dep)

    def clean_deps(self, deps):
        older_deps = ETLBlood.objects.filter(child_id=self.id, parent_id__in=deps)
        if older_deps.count() > 0:
            older_deps.delete()



class ETLBlood(models.Model):
    child = models.ForeignKey(ETLObj, on_delete=models.DO_NOTHING, related_name='child')
    parent = models.ForeignKey(ETLObj, on_delete=models.DO_NOTHING, related_name='parent')
    ctime = models.DateTimeField(default=timezone.now)
    current = 0

    def __str__(self):
        return self.parent.name + '-->' + self.child.name


class TblBlood(models.Model):
    class Meta:
        unique_together = (('tblName', 'parentTbl', 'valid'),)

    tblName = models.CharField(max_length=100, db_column='tbl_name')
    parentTbl = models.CharField(max_length=30, db_column='parent_tbl')
    relatedEtlId = models.IntegerField(db_column='related_etl_id')
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)
    current = 0

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
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='meta_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='meta_cgroup', null=True)

    def __str__(self):
        return self.meta


class BIUser(models.Model):
    username = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'sys_users'
        managed = False


class SqoopMysql2Hive(models.Model, ETLObjRelated):
    etl_type = 4
    name = models.CharField(max_length=40, null=False, default='none')
    mysql_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_m')
    hive_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_h')
    columns = models.TextField(null=True)
    mysql_tbl = models.CharField(max_length=300, null=False)
    option = models.TextField(null=True, )
    parallel = models.IntegerField(default=1, verbose_name='并发执行')
    where_clause = models.TextField(null=True)
    ctime = models.DateTimeField(default=timezone.now)
    partition_key = models.CharField(max_length=300, null=True, default='')
    settings = models.TextField(null=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='m2h_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='m2h_cgroup', null=True)


class SqoopHive2Mysql(models.Model, ETLObjRelated):
    etl_type = 3
    name = models.CharField(max_length=40, null=False, default='none')
    mysql_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='h2m_m')
    hive_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='h2m_h')
    columns = models.TextField(null=True)
    update_key = models.TextField(null=True)
    hive_tbl = models.CharField(max_length=300, null=False, default='none')
    mysql_tbl = models.CharField(max_length=300, null=False)
    option = models.TextField(null=True, )
    settings = models.TextField(null=True)
    partion_expr = models.TextField(null=True)
    parallel = models.IntegerField(default=1, verbose_name='并发执行')
    ctime = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='h2m_creator', null=True)
    cgroup = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name='h2m_cgroup', null=True)

    def get_deps(self):
        # TODO 依赖hive多个表，需要解析sql，目前没有这种需求，为降低错误率，暂时不支持
        return self.hive_meta.meta + '@' + self.hive_tbl


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


class SourceAppExecutions(models.Model):
    '''
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    job = models.ForeignKey(SourceApp, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)

    def __str__(self):
        return self.logLocation


class JarAppExecutions(models.Model):
    '''
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    job = models.ForeignKey(JarApp, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)
    owner = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='jar_owner', null=True)
    pid = models.IntegerField(default=-1)

    def __str__(self):
        return self.logLocation


class SqoopMysql2HiveExecutions(models.Model):
    '''
    单次任务执行记录
    '''
    logLocation = models.CharField(max_length=120, db_column='log_location')
    job = models.ForeignKey(SqoopMysql2Hive, on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=-1)

    def __str__(self):
        return self.logLocation
