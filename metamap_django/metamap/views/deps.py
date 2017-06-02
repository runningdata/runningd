# -*- coding: utf-8 -*
import logging
import os
import traceback

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from metamap.models import ExecBlood, ExecObj, SqoopHive2Mysql, SqoopMysql2Hive, NULLETL
from will_common.models import WillDependencyTask
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import AZKABAN_BASE_LOCATION, AZKABAN_SCRIPT_LOCATION

logger = logging.getLogger('django')


def edit_deps(request, pk):
    if request.method == 'POST':
        with transaction.atomic():
            new_deps = []
            for dep in request.POST.getlist('deps'):
                new_deps.append(ExecBlood(child_id=int(pk), parent_id=int(dep)))
            old_deps = ExecBlood.objects.filter(child_id=int(pk))
            for o_dep in old_deps:
                if not any(o_dep == n_dep for n_dep in new_deps):
                    o_dep.delete()

            for n_dep in new_deps:
                if not any(o_dep == n_dep for o_dep in old_deps):
                    n_dep.save()

            return HttpResponseRedirect(reverse('metamap:index'))
    else:
        obj = ExecObj.objects.get(pk=pk)
        deps = ExecBlood.objects.filter(child_id=pk)
        return render(request, 'jar/deps.html', {'deps': deps, 'obj': obj})


def generate_job_dag_v2(request, schedule, group_name='xiaov'):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        done_blood = set()
        done_leaf = set()
        folder = 'generate_job_dag_v2-' + dateutils.now_datetime()
        leafs = ExecBlood.objects.raw("SELECT 1 as id, a.* FROM "
                                      "(select DISTINCT child_id FROM metamap_execblood) a "
                                      "join ("
                                      "select rel_id from metamap_willdependencytask where `schedule` = " + schedule + " and valid=1 and type = 100 "
                                                                                                                       ") b "
                                                                                                                       "on a.child_id = b.rel_id "
                                                                                                                       "left outer join ("
                                                                                                                       "SELECT DISTINCT parent_id from metamap_execblood ) c "
                                                                                                                       "on a.child_id = c.parent_id "
                                                                                                                       "where c.parent_id is NULL")

        final_deps = set()
        leaves = set()
        for leaf in leafs:
            if leaf.child.cgroup.name == group_name:
                leaf_etl = ExecObj.objects.get(pk=leaf.child_id)
                if leaf_etl.type == 3:
                    # H2M的名字不能是hive表了，这样就跟H2H的重复了
                    etl = SqoopHive2Mysql.objects.get(pk=leaf_etl.rel_id)
                    tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl
                    job_name = 'export_' + tbl_name
                    final_deps.add(job_name)
                elif leaf_etl.type == 4:
                    etl = SqoopMysql2Hive.objects.get(pk=leaf_etl.rel_id)
                    tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl
                    job_name = 'import_' + tbl_name
                    final_deps.add(job_name)
                else:
                    final_deps.add(leaf_etl.name)
                leaves.add(leaf_etl.id)

        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        load_nodes_v2(leaves, folder, done_blood, done_leaf, schedule)

        generate_job_file_v2(ExecObj(name='etl_v2_done_' + folder), final_deps, folder, folder)
        # PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE),
        #                            '%d etls generated ' % len(done_blood))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')


def load_nodes_v2(leafs, folder, done_blood, done_leaf, schedule):
    '''
    遍历加载节点
    :param leafs:
    :param folder:
    :param done_blood:
    :return:
    '''
    for leaf in leafs:
        if leaf not in done_leaf:
            bloods = ExecBlood.objects.filter(child_id=leaf)
            print('handling leaf : %s ' % leaf)
            leaf_dependencies = set()
            parent_ids = set()
            for blood in bloods:
                parent = ExecObj.objects.get(pk=blood.parent.id)
                tasks = WillDependencyTask.objects.filter(schedule=schedule, rel_id=parent.id, valid=1, type=100)
                if tasks.count() == 1:
                    parent_ids.add(parent.id)
                    # TODO m2h 和 h2m的名字不能直接取parent的name，需要拼meta和tblname
                    if parent.type == 1:
                        print('parent is ETL %s ' % parent.name)
                        leaf_dependencies.add(parent.name)
                    elif parent.type == 3:
                        print('parent is SqoopHive2Mysql %s ' % parent.name)
                        etl = SqoopHive2Mysql.objects.get(pk=parent.rel_id)
                        tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl.lower()
                        leaf_dependencies.add('export' + tbl_name)
                    elif parent.type == 4:
                        print('parent is SqoopMysql2Hive %s ' % parent.name)
                        etl = SqoopMysql2Hive.objects.get(pk=parent.rel_id)
                        tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl.lower()
                        # TODO NAME
                        # leaf_dependencies.add('import_' + tbl_name)
                        leaf_dependencies.add(etl.name)
                    elif parent.type == 66:
                        etl = NULLETL.objects.get(pk=parent.rel_id)
                        leaf_dependencies.add('unknown_' + etl.name)
                    else:
                        print('xxxxxxxxxxxxxxx parent found..........%s' % parent.name)

            # 这里只会给给child生成job文件，而不会给他的parent生成 —— 新版本中应该生成！！！
            # 或者： 外面单独为最顶层的parent任务生成job列表
            child = ExecObj.objects.get(pk=leaf)
            generate_job_file_v2(child, leaf_dependencies, folder,
                                         schedule=schedule)
            done_leaf.add(leaf)
            load_nodes_v2(parent_ids, folder, done_blood, done_leaf, schedule)


def generate_job_file_v2(etlobj, parent_names, folder, schedule=-1):
    '''
    生成azkaban job文件
    :param blood:
    :param parent_names:
    :param folder:
    :return:
    '''
    # m2h 和 h2m的名字不能直接取parent的name，需要拼meta和tblname
    print('generating.....for job %s ' % etlobj.name)
    if etlobj.type == 1:
        job_name = etlobj.name
    elif etlobj.type == 3:
        # H2M的名字不能是hive表了，这样就跟H2H的重复了
        etl = SqoopHive2Mysql.objects.get(pk=etlobj.rel_id)
        tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl
        job_name = 'export_' + tbl_name
    elif etlobj.type == 4:
        etl = SqoopMysql2Hive.objects.get(pk=etlobj.rel_id)
        tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl
        # TODO NAME
        # job_name = 'import_' + tbl_name
        job_name = etl.name
    else:
        print('xxxxxxxxxxxxxxx parent found..........%s ' % etlobj.name)
        raise Exception('xxxxxxxxxxxxxxx parent found..........%s ')
    if not job_name.startswith('etl_v2_done_'):
        # 生成hql文件
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        # TODO 针对不同类型，生成不同文件
        # generate_etl_file(etl, location, schedule)
    command = ' echo command for ' + job_name

    # 生成job文件
    job_type = ' command\nretries=5\nretry.backoff=60000\n'
    dependencies = set()
    for p in parent_names:
        dependencies.add(p)
    content = '#' + job_name + '\n' + 'type=' + job_type + '\n' + 'command = ' + command + '\n'
    if len(dependencies) > 0:
        job_depencied = ','.join(dependencies)
        content += "dependencies=" + job_depencied + "\n"
    job_file = AZKABAN_BASE_LOCATION + folder + "/" + job_name + ".job"
    with open(job_file, 'w') as f:
        f.write(content)
    print('generating.....for jobdone %s ' % etlobj.name)