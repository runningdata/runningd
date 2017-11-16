# -*- coding: utf-8 -*
import logging
import os
import traceback

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from metamap.helpers import bloodhelper
from metamap.models import ExecBlood, ExecObj, SqoopHive2Mysql, SqoopMysql2Hive, NULLETL, ETL, TblBlood
from will_common.utils.Cycle import Graph
from will_common.models import WillDependencyTask, UserProfile
from will_common.utils import PushUtils
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import AZKABAN_BASE_LOCATION, AZKABAN_SCRIPT_LOCATION
from will_common.utils.customexceptions import RDException

logger = logging.getLogger('django')


@transaction.atomic
def edit_deps(request, pk):
    if request.method == 'POST':
        with transaction.atomic():
            new_deps = []
            new_deps_names = []
            for dep in request.POST.getlist('deps'):
                parent = ExecObj.objects.get(pk=int(dep))
                new_deps_names.append(parent.name)
                new_deps.append(ExecBlood(child_id=int(pk), parent_id=int(dep)))
            old_deps = ExecBlood.objects.filter(child_id=int(pk))
            old_deps_names = [dep.parent.name for dep in old_deps]

            for o_dep in old_deps:
                if not any(o_dep == n_dep for n_dep in new_deps):
                    o_dep.delete()

            for n_dep in new_deps:
                if not any(o_dep == n_dep for o_dep in old_deps):
                    n_dep.save()

            # TODO delete old version
            eo = ExecObj.objects.get(pk=pk)
            v1_new_deps = []
            for dep in request.POST.getlist('deps'):
                dep_name = ExecObj.objects.get(pk=dep).name
                v1_new_deps.append(TblBlood(tblName=eo.name, parentTbl=dep_name, relatedEtlId=eo.rel_id))
            v1_old_deps = TblBlood.objects.filter(relatedEtlId=eo.rel_id, valid=1)
            for o_dep in v1_old_deps:
                if not any(o_dep == n_dep for n_dep in v1_new_deps):
                    o_dep.delete()

            for n_dep in v1_new_deps:
                if not any(o_dep == n_dep for o_dep in v1_old_deps):
                    n_dep.save()

            if eo.type == 1:
                bloods = ExecBlood.objects.all()
                g = Graph(len(bloods))
                for execobj in bloods:
                    g.addEdge(execobj.parent_id, execobj.child_id)
                is_cycle, kep_path, related = bloodhelper.check_tree_cycle()
                if is_cycle:
                    raise RDException(u'提交失败，检测到环', u'关键路径：%s <br/> 相关ETL：%s' % (kep_path, '<br/>'.join(related)))
                else:
                    logger.info('cycle check passed for %s' % eo.name)

            # users = [User.objects.get(username='admin'), eo.creator.user, ]
            # for owner in eo.cgroup.owners.split(','):
            #     users.append(User.objects.get(username=owner.strip()))
            users = [UserProfile.objects.get(user=User.objects.get(username='admin')), eo.creator]
            for owner in eo.cgroup.owners.split(','):
                users.append(UserProfile.objects.get(user=User.objects.get(username=owner.strip())))

            PushUtils.push_both(users, '%s \' deps has been modified by %s. old_deps: is %s, new_deps is %s ' % (
                eo.name, request.user.username, '\n'.join(old_deps_names), '\n'.join(new_deps_names)))

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
    if schedule == '0':
        red_sche = 'day'
    elif schedule == '1':
        red_sche = 'week'
    elif schedule == '2':
        red_sche = 'month'
    else:
        red_sche = 'unknown'
    try:
        done_blood = set()
        done_leaf = set()
        folder = group_name + '-' + red_sche + '-' + dateutils.now_datetime()
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
                final_deps.add(leaf_etl.name)
                leaves.add(leaf_etl.id)

        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        load_nodes_v2(leaves, folder, done_blood, done_leaf, schedule)

        generate_job_file_v2(ExecObj(name='etl_v2_done_' + folder), final_deps, folder, schedule)

        # add no blood schedule tasks
        non_dep_task = set()
        for tsk in WillDependencyTask.objects.filter(schedule=schedule, type=100, valid=1):
            try:
                exec_obj = ExecObj.objects.get(pk=tsk.rel_id)
                if exec_obj.id not in done_leaf and (exec_obj.cgroup and exec_obj.cgroup.name == group_name):
                    generate_job_file_v2(exec_obj, list(), folder, schedule)
                    non_dep_task.add(exec_obj.name)
                elif exec_obj.type == 66:  # the NULLETL without a group id
                    generate_job_file_v2(exec_obj, list(), folder, schedule)
                    non_dep_task.add(exec_obj.name)
            except ObjectDoesNotExist, e:
                logger.error('tsk.rel_id: %d error : %s ' % (tsk.rel_id, e))

        generate_job_file_v2(ExecObj(name='etl_v2_done_nondep_' + folder), non_dep_task, folder, schedule)
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
                    leaf_dependencies.add(parent.name)

            # 这里只会给给child生成job文件，而不会给他的parent生成 —— 新版本中应该生成！！！
            # 或者： 外面单独为最顶层的parent任务生成job列表 _ ，目前是這種方式
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
    job_name = etlobj.name

    if not job_name.startswith('etl_v2_done_'):
        # 生成hql文件
        location = AZKABAN_SCRIPT_LOCATION + folder + '/' + job_name + '.hql'
        try:
            command = etlobj.get_cmd(schedule, location)
        except Exception, e:
            print('obj is :%s ' % etlobj.name)
            print traceback.format_exc()
            raise e
    else:
        command = 'done'

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
