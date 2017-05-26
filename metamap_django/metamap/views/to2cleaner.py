# -*- coding: utf-8 -*
import logging
from django.http import HttpResponse

from metamap.models import TblBlood, ETL, WillDependencyTask, ExecObj, ExecBlood, \
    SqoopMysql2Hive, AnaETL, SqoopHive2Mysql, JarApp

from will_common.utils import hivecli

logger = logging.getLogger('django')


def clean_etl(request):
    # TODO 有些sqoop import的ods表相关的，还没有生成对应的ETLBlood对象，所以当前ETL的H2H也是不完整的血统DAG
    for etl in ETL.objects.filter(valid=1):
        try:
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=1, cgroup=etl.cgroup)
            print('ETLObj for ETL done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for ETL error :%d --> %s' % (etl.id, e))
    return HttpResponse('clean_etl done')


def clean_H2M(request):
    # 把hive数据表作为自己的依赖
    for etl in SqoopHive2Mysql.objects.all():
        try:
            tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl
            etl_obj, result = ExecObj.objects.update_or_create(name=tbl_name, rel_id=etl.id, type=3)
            print('ETLObj for SqoopHive2Mysql done : %s ' % etl.name)
            rel_id = ETL.objects.get(name=tbl_name, valid=1).id
            parent = ExecObj.objects.get(rel_id=rel_id, type=1)
            etl_blood, result = ExecBlood.objects.update_or_create(child=etl_obj, parent=parent)
            print(' SqoopHive2Mysql \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print(' SqoopHive2Mysql \'s error : %d --> %s' % (etl.id, e))
    return HttpResponse('clean_H2M done')


def clean_ANA(request):
    # AnaETL清洗，顺便添加依赖(一般除了m2h就是h2h)
    for etl in AnaETL.objects.filter(valid=1):
        try:
            if etl.name.__contains__(u'转化率'):
                print(' %s passed ' % etl.name)
                continue
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=2)
            print('ETLObj for AnaETL done : %s ' % etl.name)
            # TODO 测试环境hiveserver的HDFS元数据不全面
            deps = hivecli.get_tbls(etl.query)
            for dep in deps:
                try:
                    parent = ExecObj.objects.get(name=dep, type=1)
                except Exception, e:
                    # 如果h2h里面没有，那就在m2h里
                    print(' >>>>>>>>>>>>>>>>>>>>>>>>> AnaETL s dep dep : %s ' % dep)
                    names = dep.split('@')
                    m2h = SqoopMysql2Hive.objects.get(hive_meta__meta=names[0], mysql_tbl=names[1])
                    parent = ExecObj.objects.get(rel_id=m2h.id, type=4)
                etl_blood, result = ExecBlood.objects.update_or_create(parent=parent, child=etl_obj)
                print(' AnaETL \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('ETLObj AnaETL error : %d --> %s' % (etl.id, e))
    return HttpResponse('clean_ANA done')


def clean_blood(request):
    for blood in TblBlood.objects.all():
        if blood.valid == 1:
            try:
                child = ETL.objects.get(pk=blood.relatedEtlId)
                parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                etl_blood, result = ExecBlood.objects.update_or_create(
                    child=ExecObj.objects.get(rel_id=child.id, type=1),
                    parent=ExecObj.objects.get(rel_id=parent.id,
                                               type=1))
                print(' ETL \'s ETLBlood done : %d ' % etl_blood.id)
            except Exception, e:
                print(' ETL \'s ETLBlood error : %d --> %s' % (blood.id, e))
    return HttpResponse('clean_blood done')


def clean_JAR(request):
    # jar app
    for etl in JarApp.objects.filter(valid=1):
        try:
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=6)
            print('ETLObj for JarApp done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for JarApp error :%d --> %s' % (etl.id, e))
    return HttpResponse(' clean_JAR done')


def clean_deptask(request):
    # 将既有的willdependency_task生成一遍
    for task in WillDependencyTask.objects.filter(valid=1, type=1):
        try:
            if task.type == 100:
                continue
            if ETL.objects.get(pk=task.rel_id).valid == 0:
                continue
            etl_obj = ExecObj.objects.get(type=task.type, rel_id=task.rel_id)
            WillDependencyTask.objects.update_or_create(name=task.name, rel_id=etl_obj.id, type=100,
                                                        schedule=task.schedule)
            print('WillDependencyTask done : %s' % task.name)
        except Exception, e:
            print('WillDependencyTask error : %d --> %s' % (task.id, e))
    return HttpResponse(' clean_deptask done')


def clean_M2H(request):
    for etl in SqoopMysql2Hive.objects.all():
        try:
            tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl
            etl_obj, result = ExecObj.objects.update_or_create(name=tbl_name, rel_id=etl.id, type=4)
            print('ETLObj for SqoopMysql2Hive done : %s ' % tbl_name)
            # 导入M2H，把前面缺失的import添加到ETLBlood中去
            for blood in TblBlood.objects.filter(parentTbl=tbl_name):
                try:
                    parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                except Exception, e:
                    child = ExecObj.objects.get(type=1, name=blood.tblName)
                    etl_blood, result = ExecBlood.objects.update_or_create(parent=etl_obj, child=child)
                    print(' SqoopMysql2Hive \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('SqoopMysql2Hive \'s error : %d --> %s' % (etl.id, e))
    return HttpResponse(' clean_M2H done')
