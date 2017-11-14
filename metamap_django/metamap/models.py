# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os

import re
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models

from django.template import Context
from django.template import Template
from django.utils import timezone

from metamap.db_views import ColMeta, DB
from will_common.djcelery_models import DjceleryCrontabschedule, DjceleryIntervalschedule
from will_common.models import PeriodicTask, WillDependencyTask, UserProfile, OrgGroup, CommmonCreators, CommmonTimes
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION, TMP_EXPORT_FILE_LOCATION
from will_common.utils.customexceptions import RDException

logger = logging.getLogger('django')
from will_common.utils import hivecli


class ETLObjRelated(models.Model):
    '''
    every etl obj should extend me. for example: m2h, h2h, h2m .etc
    '''
    type = 110
    name = models.CharField(max_length=100, verbose_name=u"任务名称", default='no_name_yet')
    rel_name = models.CharField(max_length=100, verbose_name=u"可读的名字", default='no_name_yet')
    ctime = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True)
    cgroup = models.ForeignKey(OrgGroup, on_delete=models.DO_NOTHING, null=True, )
    priority = models.IntegerField(default=5, blank=True)
    valid = models.IntegerField(default=1, verbose_name=u"是否生效", choices=(
        (1, '是'),
        (0, '否'),
    ))
    exec_obj = models.ForeignKey('ExecObj', on_delete=models.DO_NOTHING, null=True, )

    class Meta:
        abstract = True

    # TODO release after clean
    def save(self, *args, **kwargs):
        if self.valid != 0:
            super(ETLObjRelated, self).save(*args, **kwargs)  # Call the "real" save() method.
            # H2H与其他的ETL对象不同，其他的是在自身更新，应该以rel_id为主。而ETL以name为主，存在多版本
            # TODO
            # exe, created = ExecObj.objects.get_or_create(type=self.type, rel_id=self.id)
            # exe.name = self.name
            exe, created = ExecObj.objects.get_or_create(type=self.type, name=self.name)
            exe.rel_id = self.id
            exe.creator = self.creator
            exe.cgroup = self.cgroup
            exe.save()
            if created:
                print('exec_obj %s created for %s , id is %d ' % (exe.name, self.name, exe.id))
                logger.info('exec_obj %s created for %s' % (exe.name, self.name))
                self.exec_obj = exe
                if self.type != 66:
                    super(ETLObjRelated, self).save(*args, **kwargs)
            else:
                try:
                    print('already has exec_obj %s for %s' % (self.exec_obj.name, self.name))
                except AttributeError, e:
                    self.exec_obj = exe
                    print('already has exec_obj %s for %s, but no exec_id' % (self.exec_obj.name, self.name))
        else:
            super(ETLObjRelated, self).save(*args, **kwargs)

    def get_clean_str(self, str_list):
        return '\n'.join(str_list)

    def update_etlobj(self):
        self.clean_etlobj()
        obj, succeed = self.add_etlobj()
        obj.update_deps()
        return obj

    def add_etlobj(self):
        return ExecObj.objects.update_or_create(name=self.name, rel_id=self.id, type=self.etl_type)

    def clean_etlobj(self):
        obj = ExecObj.objects.get(rel_id=self.id, type=self.etl_type)
        if obj:
            obj.delete()

    def get_deps(self):
        '''
        这个是自动分析的依赖，不同于调度时获取的依赖，这是后者的前一个步骤，注意不要混淆了
        :return:
        '''
        return None

    def get_cmd_prefix(self):
        return "sh "

    def get_script(self, str_list, sche_vars=''):
        str_list.append("get_script Not supported now...for %s " % self.name)
        return str_list


# @receiver(post_save, sender=ETLObjRelated)
# def my_handler(sender, **kwargs):
#     if sender.valid != 0:
#         exe, created = ExecObj.objects.get_or_create(type=sender.type, name=sender.name)
#         exe.rel_id = sender.id
#         exe.creator = sender.creator
#         exe.cgroup = sender.cgroup
#         exe.save()
#         if created:
#             print('exec_obj %s created for %s , id is %d ' % (exe.name, sender.name, exe.id))
#             logger.info('exec_obj %s created for %s' % (exe.name, sender.name))
#             sender.exec_obj = exe
#         else:
#             try:
#                 print('already has exec_obj %s for %s' % (sender.exec_obj.name, sender.name))
#             except AttributeError, e:
#                 sender.exec_obj = exe
#                 print('already has exec_obj %s for %s, but no exec_id' % (sender.exec_obj.name, sender.name))
#         sender.save

class NULLETL(ETLObjRelated):
    type = 66

    # TODO release
    def save(self, *args, **kwargs):
        super(NULLETL, self).save(*args, **kwargs)  # Call the "real" save() method.
        WillDependencyTask.objects.get_or_create(name=self.name, type=100, rel_id=self.exec_obj_id, schedule=0)
        WillDependencyTask.objects.get_or_create(name=self.name, type=100, rel_id=self.exec_obj_id, schedule=1)
        WillDependencyTask.objects.get_or_create(name=self.name, type=100, rel_id=self.exec_obj_id, schedule=2)

    def get_script(self, str_list, sche_var=''):
        str_list.append("echo task for % s " % self.name)
        return str_list


class AnaETL(ETLObjRelated):
    type = 2
    headers = models.TextField(null=False, blank=False)
    query = models.TextField()
    author = models.CharField(max_length=20, blank=True, null=True)
    variables = models.CharField(max_length=2000, default='')
    auth_users = models.TextField(default='', null=False, blank=False)

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

    def get_script(self, str_list, sche_vars=''):
        # str_list.append(self.variables)
        # str_list.append(sche_vars)
        if self.name.startswith('common_'):
            part = self.name + '-' + dateutils.now_datekey()
        else:
            part = self.name + '-' + dateutils.now_datetime()
        result = TMP_EXPORT_FILE_LOCATION + part
        with open(result, 'w') as wa:
            header = self.headers
            wa.write(header.encode('gb18030'))
            wa.write('\n')
        result_dir = result + '_dir'
        pre_insertr = "insert overwrite local directory '%s' row format delimited fields terminated by ','  " % result_dir
        pre_insertr = self.variables + sche_vars + pre_insertr
        # fillename = result + '.hql'
        # with open(fillename, 'w') as fil:
        #     fil.write('set mapreduce.job.queuename=%s;' % settings.CLUTER_QUEUE)
        #     fil.write(pre_insertr.encode('utf-8'))
        sql = 'hive --hiveconf mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ' -e \"' + pre_insertr \
              + self.query.replace('"', '\\"') + '\"'
        # str_list.append('hive -f %s' % fillename)
        str_list.append(sql)
        command = 'cat %s/* | iconv -f utf-8 -c -t gb18030 >> %s' % (result_dir, result)
        str_list.append(command)
        return str_list


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


class SourceApp(ETLObjRelated):
    type = 5
    engine_type = models.ForeignKey(SourceEngine, on_delete=models.DO_NOTHING,
                                    verbose_name=u"运行工具")
    git_url = models.CharField(max_length=200, verbose_name=u"git地址")
    branch = models.CharField(max_length=20, verbose_name=u"git分支")
    sub_dir = models.CharField(max_length=100, verbose_name=u"工作目录")
    main_func = models.CharField(max_length=100, verbose_name=u"入口类")
    compile_tool = models.ForeignKey(CompileTool, on_delete=models.DO_NOTHING,
                                     verbose_name=u"运行工具")
    engine_opts = models.TextField(default='', verbose_name=u"引擎运行参数", blank=True, null=True)
    main_func_opts = models.TextField(default='', verbose_name=u"入口类运行参数", blank=True, null=True)


class JarApp(ETLObjRelated):
    type = 6
    engine_type = models.ForeignKey(SourceEngine, on_delete=models.DO_NOTHING,
                                    verbose_name=u"运行工具")
    main_func = models.CharField(max_length=100, verbose_name=u"入口类", blank=True, default='')
    jar_file = models.FileField(upload_to='jars', blank=True)
    engine_opts = models.TextField(default='', verbose_name=u"引擎运行参数", blank=True, null=True)
    main_func_opts = models.TextField(default='', verbose_name=u"入口类运行参数", blank=True, null=True)
    outputs = models.CharField(max_length=500, default='',
                               verbose_name=u"输出的表名称，目前只考虑hive表[dim_tinyv@xx_table,dim_tinyv@yy_table]", blank=True,
                               null=True)

    # TODO release after clean
    def save(self, *args, **kwargs):
        super(JarApp, self).save(*args, **kwargs)  # Call the "real" save() method.
        if self.outputs and len(self.outputs.strip()) > 0:
            new_children = list()
            for output in self.outputs.split(","):
                obj, created = NULLETL.objects.get_or_create(name=output, rel_name=output, cgroup=self.cgroup)
                obj.save()
                new_children.append(ExecBlood(child_id=obj.exec_obj.id, parent_id=self.exec_obj.id))

            old_children = ExecBlood.objects.filter(parent=self.exec_obj)
            for o_child in old_children:
                if not any(o_child == n_child for n_child in new_children):
                    o_child.delete()
            for n_child in new_children:
                if not any(o_child == n_child for o_child in old_children):
                    n_child.save()

    def get_wd(self):
        log = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-jarapp-sche-' + self.name + '.log'
        work_dir = os.path.dirname(os.path.dirname(__file__)) + '/'
        return work_dir

    def get_script(self, str_list, sche_vars=''):
        context = Context()
        context['task'] = self
        wd = self.get_wd()
        context['wd'] = wd
        if self.engine_type.id == 1:
            with open('metamap/config/spark_template.sh') as tem:
                str_list.append(tem.read())
        elif self.engine_type.id == 2:
            with open('metamap/config/hadoop_template.sh') as tem:
                str_list.append(tem.read())
        elif self.engine_type.id == 4:
            # 看看zip是否已经解压，先解压到指定目录
            zipfile = wd + self.jar_file.name
            dir = wd + 'jars/' + self.name + '/'
            if not os.path.exists(dir):
                ziputils.unzip(zipfile, dir)
            deps = [f for f in os.listdir(dir) if f.endswith('.zip') or f.endswith('.egg') or f.endswith('.py')]
            if len(deps) > 0:
                context['deps'] = ','.join(deps)
            context['wd'] = dir
            with open('metamap/config/pyspark_template.sh') as tem:
                str_list.append(tem.read())
        else:
            with open('metamap/config/jar_template.sh') as tem:
                str_list.append(tem.read())
        template = Template('\n'.join(str_list))
        strip = template.render(context).strip()
        strip = '{% load etlutils %} \n' + sche_vars + '\n' + strip
        return {strip, }


class ETL(ETLObjRelated):
    type = 1
    query = models.TextField()
    meta = models.CharField(max_length=20)
    author = models.CharField(max_length=20, blank=True, null=True)
    preSql = models.TextField(db_column='pre_sql', blank=True, null=True)
    onSchedule = models.IntegerField(default=1, db_column='on_schedule')
    setting = models.CharField(max_length=200, default='')
    variables = models.CharField(max_length=2000, default='')

    # TODO release after clean
    def save(self, *args, **kwargs):

        super(ETL, self).save(*args, **kwargs)
        if self.valid != 0:
            new_deps = []
            for dep in self.get_deps():
                print('handing dep : %s' % dep)
                try:
                    etl = ETL.objects.get(name=dep, valid=1)
                except ObjectDoesNotExist:
                    try:
                        etl = SqoopMysql2Hive.objects.get(rel_name=dep, valid=1)
                    except ObjectDoesNotExist:
                        try:
                            etl = NULLETL.objects.get(name=dep, valid=1)
                        except ObjectDoesNotExist, e:
                            raise RDException(u'依赖{dep}尚未录入系统'.format(dep=dep))
                    except MultipleObjectsReturned:
                        raise RDException(u'发现多个M2H对象:{dep}, M2H只能有一个目标表为{dep}, 请酌情处理'.format(dep=dep))
                if self.exec_obj.id != etl.exec_obj.id:
                    new_deps.append(ExecBlood(child_id=self.exec_obj.id, parent_id=etl.exec_obj.id))

            old_deps = ExecBlood.objects.filter(child_id=self.exec_obj.id)
            for o_dep in old_deps:
                if not any(o_dep == n_dep for n_dep in new_deps):
                    o_dep.delete()
            for n_dep in new_deps:
                if not any(o_dep == n_dep for o_dep in old_deps):
                    n_dep.save()

    def __str__(self):
        return self.name + '_' + str(self.id)

    def get_script(self, str_list, sche_vars=''):
        str_list.append(self.variables)
        str_list.append(sche_vars)
        str_list.append("-- job for " + self.name)
        if self.creator:
            str_list.append("-- " + self.creator.user.username + '-' + self.name)
        if self.author:
            str_list.append("-- author : " + self.author)
        ctime = self.ctime
        if (ctime != None):
            str_list.append("-- create time : " + dateutils.format_day(ctime))
        else:
            str_list.append("-- cannot find ctime")
        str_list.append("\n---------------------------------------- pre settings ")
        str_list.append(self.setting)
        str_list.append('set mapreduce.job.queuename=' + settings.CLUTER_QUEUE + ';')
        str_list.append("\n---------------------------------------- preSql ")
        str_list.append(self.preSql)
        str_list.append("\n---------------------------------------- query ")
        str_list.append(self.query)
        return str_list

    def get_cmd_prefix(self):
        return "hive -f "

    def get_deps(self):
        deps = hivecli.getTbls_v2(self)
        return deps


class ExecObj(models.Model):
    '''
    最終確定還是使用ETL的名字吧，不去分析具體的表名字了
    '''
    name = models.CharField(max_length=100, db_column='name')
    type = models.IntegerField(default=1, blank=False, null=False,
                               help_text="1 ETL; 2 EMAIL; 3 Hive2Mysql; 4 Mysql2Hive; 5 sourcefile;6 jarfile")
    rel_id = models.IntegerField(default=1)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='etl_v2_creator', null=True)
    cgroup = models.ForeignKey(OrgGroup, on_delete=models.DO_NOTHING, related_name='etl_v2_cgroup', null=True)

    def execute(self):
        self.get_rel_obj().execute()

    def get_cmd(self, schedule, location):
        obj = self.get_rel_obj()
        str_list = list()
        str_list.append('{% load etlutils %}')
        sche_vars = ''
        if schedule != -1:
            tt = WillDependencyTask.objects.get(rel_id=self.id, schedule=schedule, type=100)
            sche_vars = tt.variables
        str_list = obj.get_script(str_list, sche_vars)
        template = Template(obj.get_clean_str(str_list))
        script = template.render(Context()).strip()
        with open(location, 'w') as sc:
            sc.write(script.encode('utf8'))
        command = obj.get_cmd_prefix() + location
        if not settings.USE_ROOT:
            command = 'runuser -l ' + self.cgroup.name + ' -c "' + command + '"'
        return command

    def get_deps(self):
        return ExecBlood.objects.filter(child=self)

    def get_rel_obj(self):
        if self.type == 1:
            return ETL.objects.get(pk=self.rel_id)
        elif self.type == 2:
            return AnaETL.objects.get(pk=self.rel_id)
        elif self.type == 3:
            return SqoopHive2Mysql.objects.get(pk=self.rel_id)
        elif self.type == 4:
            return SqoopMysql2Hive.objects.get(pk=self.rel_id)
        elif self.type == 5:
            return SourceApp.objects.get(pk=self.rel_id)
        elif self.type == 6:
            return JarApp.objects.get(pk=self.rel_id)
        elif self.type == 66:
            return NULLETL.objects.get(pk=self.rel_id)
        else:
            return None

    def update_deps(self):
        '''
        better use this
        :param deps:
        :return:
        '''
        # TODO swith dict
        etl = ETL.objects.get(pk=self.rel_id)
        deps = etl.get_deps()
        dep_ids = [ExecObj.objects.get(name=dep).id for dep in deps]
        self.clean_deps(dep_ids)
        self.add_deps(dep_ids)
        logger.info('ETLBlood has been created successfully : %s' % deps)

    def add_deps(self, deps):
        for dep in deps:
            ExecBlood.objects.update_or_create(child_id=self.id, parent_id=dep)

    def clean_deps(self, deps):
        older_deps = ExecBlood.objects.filter(child_id=self.id, parent_id__in=deps)
        if older_deps.count() > 0:
            older_deps.delete()


class ExecBlood(models.Model):
    child = models.ForeignKey(ExecObj, on_delete=models.DO_NOTHING, related_name='child')
    parent = models.ForeignKey(ExecObj, on_delete=models.DO_NOTHING, related_name='parent')
    ctime = models.DateTimeField(default=timezone.now)

    def __eq__(self, other):
        return self.child.id == other.child.id and self.parent.id == other.parent.id

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

    def __eq__(self, other):
        return self.relatedEtlId == other.relatedEtlId and self.parentTbl == other.parentTbl and self.valid == other.valid

    def __str__(self):
        return self.parentTbl + '-->' + self.tblName


class Meta(models.Model):
    '''
       数据库对应meta
    '''
    meta = models.CharField(max_length=30, unique=True)
    db = models.CharField(max_length=30)
    settings = models.CharField(max_length=300, null=True)
    type = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)
    creator = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='meta_creator', null=True)
    cgroup = models.ForeignKey(OrgGroup, on_delete=models.DO_NOTHING, related_name='meta_cgroup', null=True)

    def __str__(self):
        return self.meta


class BIUser(models.Model):
    username = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'sys_users'
        managed = False


class SqoopMysql2Hive(ETLObjRelated):
    type = 4
    mysql_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_m')
    hive_meta = models.ForeignKey(Meta, on_delete=models.DO_NOTHING, null=False, related_name='m2h_h')
    columns = models.TextField(null=True)
    mysql_tbl = models.CharField(max_length=300, null=False)
    option = models.TextField(null=True, )
    parallel = models.IntegerField(default=1, verbose_name='并发执行')
    where_clause = models.TextField(null=True)
    partition_key = models.CharField(max_length=300, null=True, default='')
    settings = models.TextField(null=True)

    # TODO release this after clean all data
    def save(self, *args, **kwargs):
        tbl_name = self.hive_meta.meta + '@' + self.mysql_tbl.lower()
        if 'hive-table' in self.option:
            for op in self.option.split('--'):
                if op.startswith('hive-table'):
                    tbl_name = self.hive_meta.meta + '@' + re.split('\s', op.strip())[1].lower()
                    break
        self.rel_name = tbl_name
        super(SqoopMysql2Hive, self).save(*args, **kwargs)

    def get_clean_str(self, str_list):
        return ' '.join(str_list).replace('\n', ' ').replace('&', '\&')

    def get_hive_inmi_tbl(self, tbl):
        return tbl + '_inmi'

    def get_script(self, str_list, sche_vars=''):
        is_partition = True if len(self.partition_key) > 0 else False
        str_list.append(self.settings)
        str_list.append(sche_vars)
        str_list.append(' sqoop import ')
        str_list.append('-Dmapreduce.job.queuename=' + settings.CLUTER_QUEUE)
        str_list.append(self.mysql_meta.settings)
        str_list.append(' --hive-database ')
        str_list.append(self.hive_meta.db)
        if self.columns:
            str_list.append(' --columns')
            str_list.append(self.columns)
        if self.where_clause:
            str_list.append(' --where')
            str_list.append(self.where_clause)
        str_list.append(' --table')
        if is_partition:
            str_list.append(self.mysql_tbl)
            str_list.append(' --hive-table ' + self.get_hive_inmi_tbl(self.mysql_tbl))
        else:
            str_list.append(self.mysql_tbl)
        str_list.append(' --hive-import --hive-overwrite')
        str_list.append(' --target-dir ')
        str_list.append(self.hive_meta.meta + '_' + self.name)
        str_list.append('--outdir /server/app/sqoop/vo --bindir /server/app/sqoop/vo --verbose ')
        str_list.append(' -m %d ' % self.parallel)
        if 'target-dir' in self.option:
            export_dir = DB.objects.using('hivemeta').filter(name=self.hive_meta.db).first().db_location_uri
            export_dir += '/'
            export_dir += self.mysql_tbl
            export_dir += '/'
            str_list.append(self.option.replace('target-dir', 'target-dir ' + export_dir))
        else:
            str_list.append(' --delete-target-dir ')
            str_list.append(self.option)

        return str_list


class SqoopHive2Mysql(ETLObjRelated):
    type = 3
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

    # TODO release this after clean all data
    def save(self, *args, **kwargs):
        self.rel_name = self.hive_meta.meta + '@' + self.hive_tbl.lower()
        super(SqoopHive2Mysql, self).save(*args, **kwargs)
        parent = ExecObj.objects.get(name=self.rel_name, type=ETL.type)
        print('SqoopHive2Mysql: child is %s , parent is %s' % (self.exec_obj.name, parent.name))
        logger.error('SqoopHive2Mysql: child is %s , parent is %s' % (self.exec_obj.name, parent.name))
        ExecBlood.objects.get_or_create(child=self.exec_obj, parent=parent)

    def get_clean_str(self, str_list):
        return ' '.join(str_list).replace('\n', ' ').replace('&', '\&')

    def get_deps(self):
        # TODO 依赖hive多个表，需要解析sql，目前没有这种需求，为降低错误率，暂时不支持
        return self.hive_meta.meta + '@' + self.hive_tbl

    def get_script(self, str_list, sche_vars=''):
        str_list.append(self.settings)
        str_list.append(sche_vars)
        str_list.append(' sqoop export ')
        str_list.append('-Dmapreduce.job.queuename=' + settings.CLUTER_QUEUE)
        str_list.append(self.mysql_meta.settings)
        if 'input-fields-terminated-by' not in self.option:
            str_list.append(' --input-fields-terminated-by "\\t" ')
        str_list.append('  --update-key ')
        str_list.append(self.update_key)
        str_list.append(' --update-mode allowinsert ')
        str_list.append(' --columns ')
        str_list.append(self.columns)
        if not settings.DEBUG:
            export_dir = ColMeta.objects.using('hivemeta').filter(db__name=self.hive_meta.db,
                                                                  tbl__tbl_name=self.hive_tbl).first().location
        else:
            export_dir = ''
        export_dir += '/'
        export_dir += self.hive_tbl
        export_dir += '/'
        if len(self.partion_expr) != 0:
            export_dir += self.partion_expr
        str_list.append(' --export-dir ')
        str_list.append(export_dir)
        str_list.append(' --table ')
        str_list.append(self.mysql_tbl)
        str_list.append(' --verbose ')
        str_list.append(' -m %d ' % self.parallel)
        str_list.append(self.option)
        return str_list


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


class ExecutionsV2(models.Model):
    log_location = models.CharField(max_length=120)
    job = models.ForeignKey(ExecObj, on_delete=models.CASCADE, null=False)
    cmd_shot = models.TextField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(default=0)


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


class WillTaskV2(CommmonCreators, CommmonTimes):
    name = models.CharField(unique=True, max_length=200)
    valid = models.IntegerField(default=1)
    variables = models.TextField()
    desc = models.TextField()
    tasks = models.ManyToManyField(ExecObj)

    def get_schedule(self):
        task = PeriodicTask.objects.get(name=self.name)
        cron = task.crontab
        return cron.minute + ' ' + cron.hour + ' ' + cron.day_of_month + ' ' + cron.month_of_year + ' ' + cron.day_of_week

# class WillDepTask_v2(models.Model):
#     name = models.CharField(unique=True, max_length=200)
#     schedule = models.IntegerField(null=False, default=1)  # 0 天 1 周 2 月 3 季度 4 cron
#     valid = models.IntegerField(default=1)
#     ctime = models.DateTimeField(default=timezone.now)
#     utime = models.DateTimeField(null=True)
#     variables = models.TextField()
#     desc = models.TextField()
#     executable = models.ForeignKey(ExecObj, on_delete=models.DO_NOTHING, related_name='jar_owner', null=True)
#
#     def get_schedule(self):
#         task = PeriodicTask.objects.get(willtask_id=self.id)
#         if self.schedule == 4:
#             cron = task.crontab
#             return cron.minute + ' ' + cron.hour + ' ' + cron.day_of_month + ' ' + cron.month_of_year + ' ' + cron.day_of_week
#         else:
#             return ''
