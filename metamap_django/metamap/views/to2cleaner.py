# -*- coding: utf-8 -*
import logging

import re
import traceback
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from metamap.models import TblBlood, ETL, WillDependencyTask, ExecObj, ExecBlood, \
    SqoopMysql2Hive, AnaETL, SqoopHive2Mysql, JarApp, NULLETL, Exports, ExecutionsV2
from will_common.models import PeriodicTask
from will_common.templatetags import etlutils

logger = logging.getLogger('django')


@transaction.atomic
def clean_etl(request):
    # TODO 有些sqoop import的ods表相关的，还没有生成对应的ETLBlood对象，所以当前ETL的H2H也是不完整的血统DAG
    for etl in ETL.objects.filter(valid=1):
        try:
            etl_obj, result = ExecObj.objects.get_or_create(name=etl.name, rel_id=etl.id, type=1, cgroup=etl.cgroup,
                                                            creator=etl.creator)
            print('ETLObj for ETL done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for ETL error :%d --> %s' % (etl.id, e))
    return HttpResponse('clean_etl done')


@transaction.atomic
def clean_H2M(request):
    # 把hive数据表作为自己的依赖
    for etl in SqoopHive2Mysql.objects.filter(valid=1):
        try:
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=3, cgroup=etl.cgroup,
                                                               creator=etl.creator)
            print('ETLObj for SqoopHive2Mysql done : %s ' % etl.name)
            rel_id = ETL.objects.get(name=etl.rel_name, valid=1).id
            parent = ExecObj.objects.get(rel_id=rel_id, type=1)
            etl_blood, result = ExecBlood.objects.update_or_create(child=etl_obj, parent=parent)
            print(' SqoopHive2Mysql \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print(' SqoopHive2Mysql \'s error : %d --> %s' % (etl.id, e))
    return HttpResponse('clean_H2M done')


@transaction.atomic
def clean_ANA(request):
    # AnaETL清洗，顺便添加依赖(一般除了m2h就是h2h)
    for etl in AnaETL.objects.filter(valid=1):
        try:
            # if etl.name.__contains__(u'转化率'):
            #     print(' %s passed ' % etl.name)
            #     continue
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=2, cgroup=etl.cgroup,
                                                               creator=etl.creator)
            print('ETLObj for AnaETL done : %s ' % etl.name)
            # TODO 测试环境hiveserver的HDFS元数据不全面
            # deps = hivecli.get_tbls(etl.query)
            # for dep in deps:
            #     try:
            #         parent = ExecObj.objects.get(name=dep, type=1)
            #     except Exception, e:
            #         # 如果h2h里面没有，那就在m2h里
            #         print(' >>>>>>>>>>>>>>>>>>>>>>>>> AnaETL s dep dep : %s ' % dep)
            #         names = dep.split('@')
            #         m2h = SqoopMysql2Hive.objects.get(hive_meta__meta=names[0], mysql_tbl=names[1])
            #         parent = ExecObj.objects.get(rel_id=m2h.id, type=4)
            #     etl_blood, result = ExecBlood.objects.update_or_create(parent=parent, child=etl_obj)
            #     print(' AnaETL \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('ETLObj AnaETL error : %d --> %s' % (etl.id, e))
    return HttpResponse('clean_ANA done')


@transaction.atomic
def clean_etlp_befor_blood(request):
    '''
    先清洗所有不是ETL的父节点
    :param request:
    :return:
    '''
    for blood in TblBlood.objects.all():
        if blood.valid == 1:
            try:
                '''
                如果不是ETL，那么先看看是不是M2H，如果不是M2H，就暂时搁置为NULLETL， 并创建与之相关联的ExecObj,加入ExecBlood
                '''
                try:
                    parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                except ObjectDoesNotExist, e:
                    try:
                        SqoopMysql2Hive.objects.get(rel_name=blood.parentTbl)
                    except ObjectDoesNotExist, e:
                        child = ETL.objects.get(pk=blood.relatedEtlId)
                        parent, status = NULLETL.objects.get_or_create(name=blood.parentTbl, rel_name=blood.parentTbl)
                        ExecObj.objects.get_or_create(name=parent.name, rel_id=parent.id, type=NULLETL.type,
                                                      cgroup=child.cgroup)
                        logger.error(e.message)
            except Exception, e:
                print(' ETL \'s ETLBlood error : %d --> %s' % (blood.id, e))

    return HttpResponse('clean_blood done')


@transaction.atomic
def clean_blood(request):
    for blood in TblBlood.objects.all():
        if blood.valid == 1 and blood.parentTbl != '_dummy_database@_dummy_table':
            try:
                child = ETL.objects.get(pk=blood.relatedEtlId)
                '''
                如果不是ETL，那么先看看是不是M2H，如果不是M2H，就暂时搁置为NULLETL， 并创建与之相关联的ExecObj,加入ExecBlood
                '''
                try:
                    parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                except ObjectDoesNotExist, e:
                    try:
                        # parent = SqoopMysql2Hive.objects.get(name=blood.parentTbl, valid=1)
                        parent = SqoopMysql2Hive.objects.get(rel_name=blood.parentTbl)
                    except ObjectDoesNotExist, e:
                        parent = NULLETL.objects.get(name=blood.parentTbl)
                        logger.error(e.message)
                cc = ExecObj.objects.get(rel_id=child.id, type=1)
                pp = ExecObj.objects.get(name=parent.name)
                etl_blood, result = ExecBlood.objects.update_or_create(
                    child=cc,
                    parent=pp)
                print(' ETL \'s ETLBlood done : %d ' % etl_blood.id)
            except Exception, e:
                print(' ETL \'s ETLBlood error : %d --> %s' % (blood.id, e))

    # for h2m in ExecObj.objects.filter(type=3):
    #     hm = SqoopHive2Mysql.objects.get(pk=h2m.rel_id)
    #     if hm.rel_name == '_dummy_database@_dummy_table':
    #         continue
    #     try:
    #         pp = ExecObj.objects.get(name=hm.rel_name)
    #     except ObjectDoesNotExist, e:
    #         parent, created = NULLETL.objects.get_or_create(name=blood.parentTbl, rel_name=blood.parentTbl)
    #         pp, created = ExecObj.objects.get_or_create(name=hm.name, rel_id=parent.id, type=parent.type, creator=hm.creator, cgroup=hm.cgroup)
    #         logger.error(e.message)
    #
    #     cc, status = ExecObj.objects.get_or_create(name=h2m.name, rel_id=h2m.id, type=3, creator=hm.creator, cgroup=hm.cgroup)
    #     ExecBlood.objects.update_or_create(
    #         child=cc,
    #         parent=pp)
    #     print('add blood for h2m : %s , h2m id is : %d ' % (hm.rel_name, h2m.rel_id))
    return HttpResponse('clean_blood done')


@transaction.atomic
def clean_JAR(request):
    # jar app
    for etl in JarApp.objects.filter(valid=1):
        try:
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=6, cgroup=etl.cgroup,
                                                               creator=etl.creator)

            # exexobj = ExecObj.objects.get(name=etl.name, rel_id = etl.id, type = 6)
            # exexobj.cgroup = etl.cgroup
            # exexobj.creator = etl.creator
            # exexobj.save()

            print('ETLObj for JarApp done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for JarApp error :%d --> %s' % (etl.id, e))
    return HttpResponse(' clean_JAR done')


@transaction.atomic
def clean_deptask(request):
    # 将既有的willdependency_task生成一遍
    # for task in WillDependencyTask.objects.filter(valid=1, type=1):
    #     try:
    #         if task.type == 100:
    #             continue
    #         if ETL.objects.get(pk=task.rel_id).valid == 0:
    #             continue
    #         etl_obj = ExecObj.objects.get(type=task.type, rel_id=task.rel_id)
    #         WillDependencyTask.objects.update_or_create(name=task.name, rel_id=etl_obj.id, type=100,
    #                                                     schedule=task.schedule)
    #         print('WillDependencyTask done : %s' % task.name)
    #     except Exception, e:
    #         print('WillDependencyTask error : %d --> %s' % (task.id, e))

    type = int(request.GET['type'])
    for task in WillDependencyTask.objects.filter(valid=1, type=type):
        try:
            if task.type == 100:
                continue
            try:
                if SqoopMysql2Hive.objects.get(pk=task.rel_id).valid == 0:
                    continue
            except ObjectDoesNotExist, e:
                pass
            etl_obj = ExecObj.objects.get(type=task.type, rel_id=task.rel_id)
            WillDependencyTask.objects.update_or_create(name=task.name, rel_id=etl_obj.id, type=100,
                                                        schedule=task.schedule, variables=task.variables,
                                                        desc=task.desc)
            print('WillDependencyTask done : %s' % task.name)
        except Exception, e:
            print('WillDependencyTask error : %d --> %s' % (task.id, e))
    return HttpResponse(' clean_deptask done')


@transaction.atomic
def clean_null(request):
    for null in NULLETL.objects.all():
        print null.name
        null_obj = ExecObj.objects.get(type=NULLETL.type, rel_id=null.id)
        WillDependencyTask.objects.update_or_create(name=null_obj.name, type=100, rel_id=null_obj.id, schedule=0)
        WillDependencyTask.objects.update_or_create(name=null_obj.name, type=100, rel_id=null_obj.id, schedule=1)
        WillDependencyTask.objects.update_or_create(name=null_obj.name, type=100, rel_id=null_obj.id, schedule=2)
    return HttpResponse('ulll done')


@transaction.atomic
def clean_M2H(request):
    for etl in SqoopMysql2Hive.objects.all():
        try:
            etl_obj, result = ExecObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=4, cgroup=etl.cgroup,
                                                               creator=etl.creator)
            print('ETLObj for SqoopMysql2Hive done : %s ' % etl.name)

            # 导入M2H，把前面缺失的import添加到ETLBlood中去
            for blood in TblBlood.objects.filter(parentTbl=etl.rel_name):
                try:
                    parent = ETL.objects.get(rel_name=blood.parentTbl, valid=1)
                except Exception, e:
                    child = ExecObj.objects.get(type=1, name=blood.tblName)
                    etl_blood, result = ExecBlood.objects.update_or_create(parent=etl_obj, child=child)
                    print(' SqoopMysql2Hive \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('SqoopMysql2Hive \'s error : %d --> %s' % (etl.id, e))
    return HttpResponse(' clean_M2H done')


@transaction.atomic
def clean_rel_name(request):
    '''
    清洗M2H和H2M的名字，方便後面過濾查取等
    :param request:
    :return:
    '''
    for etl in SqoopMysql2Hive.objects.all():
        tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl.lower()
        if 'hive-table' in etl.option:
            for op in etl.option.split('--'):
                if op.startswith('hive-table'):
                    tbl_name = etl.hive_meta.meta + '@' + re.split('\s', op.strip())[1].lower()
                    break
        etl.rel_name = tbl_name
        etl.save()

    for etl in SqoopHive2Mysql.objects.all():
        tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl.lower()
        etl.rel_name = tbl_name
        etl.save()
    return HttpResponse('XX')


def clean_etl_group(requset):
    for etl in ETL.objects.filter(valid=1):
        try:
            eo = ExecObj.objects.get(type=1, rel_id=etl.id)
            eo.creator = etl.creator
            eo.cgroup = etl.cgroup
            eo.save()
        except:
            print('error for %s ' % etl.name)
    return HttpResponse('XX')


@transaction.atomic
def clean_period_tsk(request):
    current_tsk = 0
    try:
        for ptask in PeriodicTask.objects.filter(willtask_id__gt=0):
            o_wtask = WillDependencyTask.objects.get(pk=ptask.willtask_id)
            current_tsk = ptask.id
            try:
                exec_obj = ExecObj.objects.get(type=o_wtask.type, rel_id=o_wtask.rel_id)
                n_wtask = WillDependencyTask.objects.get(rel_id=exec_obj.id, type=100)
            except ObjectDoesNotExist, e:
                print('mark for %s ' % o_wtask.name)
                continue
            ptask.task = 'metamap.tasks.exec_etl_cli2'
            ptask.args = ptask.args.replace(str(o_wtask.id), str(n_wtask.id))
            ptask.willtask_id = n_wtask.id
            ptask.save()
    except:
        print('current id is %d ' % current_tsk)
        print traceback.format_exc()
    return HttpResponse('pTASK DONE')


@transaction.atomic
def clean_exec_obj_id(request):
    '''
    all test has passed, before release all save method for ETLRelatedObjs. then execute this
    :param request:
    :return:
    '''
    for execobj in ExecObj.objects.all():
        if execobj.type == 1:
            etl = ETL.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        elif execobj.type == 2:
            etl = AnaETL.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        elif execobj.type == 3:
            etl = SqoopHive2Mysql.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        elif execobj.type == 4:
            etl = SqoopMysql2Hive.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        elif execobj.type == 6:
            etl = JarApp.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        elif execobj.type == 66:
            etl = NULLETL.objects.get(id=execobj.rel_id)
            etl.exec_obj_id = execobj.id
            etl.save()
        else:
            print('errrrrrrrrrrrrrrrrrrrrrrrrr : %s ' % execobj.name)
    return HttpResponse('EXEC OBJ CLEAN DONE')


def clean_all(request):
    # clean_rel_name(request)
    clean_etl(request)
    clean_etlp_befor_blood(request)
    clean_blood(request)
    clean_M2H(request)
    # request.GET['type'] = 1
    # clean_deptask(request)
    # request.GET['type'] = 4
    # clean_deptask(request)
    return HttpResponse('All Done')


def clean_group(request):
    result = list()
    nullobj = list()
    for eo in ExecObj.objects.all():
        if eo.type == 1:
            etl = ETL.objects.get(pk=eo.rel_id)
        elif eo.type == 2:
            etl = AnaETL.objects.get(pk=eo.rel_id)
        elif eo.type == 3:
            etl = SqoopHive2Mysql.objects.get(pk=eo.rel_id)
        elif eo.type == 4:
            etl = SqoopMysql2Hive.objects.get(pk=eo.rel_id)
        elif eo.type == 6:
            etl = JarApp.objects.get(pk=eo.rel_id)
        elif eo.type == 66:
            nullobj.append(eo.name)

        if etl.cgroup_id != eo.cgroup_id:
            eo.cgroup_id = etl.cgroup_id
            # eo.save()
            result.append(eo.name)
        print '\n'.join(nullobj)
    return HttpResponse('<br/>'.join(result))


def clean_exports(request):
    now = timezone.now()
    days = now - datetime.timedelta(days=7)
    objs = Exports.objects.filter(start_time__gt=days).order_by('-start_time')
    result = list()
    err_list = list()
    with transaction.atomic():
        for obj in objs:
            try:
                task = WillDependencyTask.objects.get(pk=obj.task_id)
                if task.type == 2:
                    exec_obj = ExecObj.objects.get(type=2, rel_id=task.rel_id)
                elif task.type == 100:
                    exec_obj = ExecObj.objects.get(id=task.rel_id)
                ExecutionsV2.objects.get_or_create(log_location=obj.file_loc, start_time=obj.start_time,
                                                   end_time=obj.end_time, job=exec_obj, status=1)
                result.append(obj.file_loc)
            except Exception, e:
                traceback.print_exc(e)
                err_list.append(obj.file_loc)
        for er in err_list:
            print er
    return HttpResponse('<br/>'.join(result))
