# -*- coding: utf-8 -*
import base64
import json
import logging
import os
import traceback
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import BadHeaderError
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import FileResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from metamap.helpers import bloodhelper, etlhelper
from metamap.models import TblBlood, ETL, Executions, WillDependencyTask, ETLObj, ETLBlood, SqoopHive2Mysql, \
    SqoopMysql2Hive, AnaETL, JarApp

from will_common.utils import PushUtils
from will_common.utils import constants
from will_common.utils import encryptutils
from will_common.utils import hivecli, httputils, dateutils, ziputils
from will_common.utils import userutils
from will_common.utils.constants import *
from will_common.views.common import GroupListView

logger = logging.getLogger('django')


# work_manager = threadpool.WorkManager(10, 3)

@method_decorator(login_required, name='dispatch')
class IndexView(GroupListView):
    template_name = 'index.html'
    context_object_name = 'etls'
    model = ETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ETL.objects.filter(valid=1, name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        current_group = self.request.user.groups.all()
        return ETL.objects.filter(valid=1).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


def clean_etl_data(request):
    # TODO 有些sqoop import的ods表相关的，还没有生成对应的ETLBlood对象，所以当前ETL的H2H也是不完整的血统DAG
    for etl in ETL.objects.filter(valid=1):
        try:
            etl_obj, result = ETLObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=1)
            print('ETLObj for ETL done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for ETL error :%d --> %s' % (etl.id, e))

    for blood in TblBlood.objects.all():
        if blood.valid == 1:
            try:
                child = ETL.objects.get(pk=blood.relatedEtlId)
                parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                etl_blood, result = ETLBlood.objects.update_or_create(child=ETLObj.objects.get(rel_id=child.id, type=1), parent=ETLObj.objects.get(rel_id=parent.id, type=1))
                print(' ETL \'s ETLBlood done : %d ' % etl_blood.id)
            except Exception, e:
                print(' ETL \'s ETLBlood error : %d --> %s' % (blood.id, e))

    # 把hive数据表作为自己的依赖
    for etl in SqoopHive2Mysql.objects.all():
        try:
            tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl
            etl_obj, result = ETLObj.objects.update_or_create(name=tbl_name, rel_id=etl.id, type=3)
            print('ETLObj for SqoopHive2Mysql done : %s ' % etl.name)
            rel_id = ETL.objects.get(name=tbl_name, valid=1).id
            parent = ETLObj.objects.get(rel_id=rel_id, type=1)
            etl_blood, result = ETLBlood.objects.update_or_create(child=etl_obj, parent=parent)
            print(' SqoopHive2Mysql \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print(' SqoopHive2Mysql \'s error : %d --> %s' % (etl.id, e))


    for etl in SqoopMysql2Hive.objects.all():
        try:
            tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl
            etl_obj, result = ETLObj.objects.update_or_create(name=tbl_name, rel_id=etl.id, type=4)
            print('ETLObj for SqoopMysql2Hive done : %s ' % tbl_name)
            # 导入M2H，把前面缺失的import添加到ETLBlood中去
            for blood in TblBlood.objects.filter(parentTbl=tbl_name):
                try:
                    parent = ETL.objects.get(name=blood.parentTbl, valid=1)
                except Exception, e:
                    child = ETLObj.objects.get(type=1, name=blood.tblName)
                    etl_blood, result = ETLBlood.objects.update_or_create(parent=etl_obj, child=child)
                    print(' SqoopMysql2Hive \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('SqoopMysql2Hive \'s error : %d --> %s' % (etl.id, e))

    # AnaETL清洗，顺便添加依赖(一般除了m2h就是h2h)
    for etl in AnaETL.objects.filter(valid=1):
        try:
            if etl.name.__contains__(u'转化率'):
                print(' %s passed ' % etl.name)
                continue
            etl_obj, result = ETLObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=2)
            print('ETLObj for AnaETL done : %s ' % etl.name)
            # TODO 测试环境hiveserver的HDFS元数据不全面
            deps = hivecli.get_tbls(etl.query)
            for dep in deps:
                try:
                    parent = ETLObj.objects.get(name=dep, type=1)
                except Exception, e:
                    # 如果h2h里面没有，那就在m2h里
                    print(' >>>>>>>>>>>>>>>>>>>>>>>>> AnaETL s dep dep : %s ' % dep)
                    names = dep.split('@')
                    m2h = SqoopMysql2Hive.objects.get(hive_meta__meta=names[0], mysql_tbl=names[1])
                    parent = ETLObj.objects.get(rel_id=m2h.id, type=4)
                etl_blood, result = ETLBlood.objects.update_or_create(parent=parent, child=etl_obj)
                print(' AnaETL \'s ETLBlood done : %d ' % etl_blood.id)
        except Exception, e:
            print('ETLObj AnaETL error : %d --> %s' % (etl.id, e))

    # jar app
    for etl in JarApp.objects.filter(valid=1):
        try:
            etl_obj, result = ETLObj.objects.update_or_create(name=etl.name, rel_id=etl.id, type=6)
            print('ETLObj for JarApp done : %s ' % etl.name)
        except Exception, e:
            print('ETLObj for JarApp error :%d --> %s' % (etl.id, e))

    # 将既有的willdependency_task生成一遍
    for task in WillDependencyTask.objects.filter(valid=1):
        try:
            if task.type == 100:
                continue
            etl_obj = ETLObj.objects.get(type=task.type, rel_id=task.rel_id)
            WillDependencyTask.objects.update_or_create(name=task.name, rel_id=etl_obj.id, type=100, schedule=task.schedule)
            print('WillDependencyTask done : %s' % task.name)
        except Exception, e:
            print('WillDependencyTask error : %d --> %s' % (task.id, e))
    return HttpResponse('done')


def get_json(request):
    queryset = ETL.objects.filter(valid=1).order_by('-ctime')
    io = StringIO()
    json.dump(queryset, io)
    from django.core import serializers
    data = serializers.serialize('json ', queryset)
    return HttpResponse(data, mimetype="application/json")


class InvalidView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'etls'
    model = ETL

    def get_queryset(self):
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            tbl_name_ = self.request.GET['search']
            return ETL.objects.filter(valid=0, name__contains=tbl_name_).order_by('-ctime')
        self.paginate_by = DEFAULT_PAGE_SIEZE
        return ETL.objects.filter(valid=0).order_by('-ctime')

    def get_context_data(self, **kwargs):
        context = super(InvalidView, self).get_context_data(**kwargs)
        if 'search' in self.request.GET and self.request.GET['search'] != '':
            context['search'] = self.request.GET['search']
        return context


class EditView(generic.DetailView):
    template_name = 'etl/edit.html'
    context_object_name = 'form'
    queryset = ETL.objects.all()


def blood_dag(request, etlid):
    bloods = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1)
    final_bloods = set()
    p_depth, c_depth = 0, 0
    p_depth = int(request.GET.get('p_depth', default=0))
    c_depth = int(request.GET.get('c_depth', default=0))
    for blood in bloods:
        blood.current = blood.id
        if p_depth != -1:
            final_bloods.add(blood)
            bloodhelper.find_parent_mermaid(blood, final_bloods, depth=p_depth)
        if c_depth != -1:
            bloodhelper.find_child_mermaid(blood, final_bloods, depth=c_depth)
    return render(request, 'etl/blood.html', {'bloods': final_bloods})



def blood_by_name(request):
    etl_name = request.GET['tblName']
    try:
        etl = ETL.objects.filter(valid=1).get(name=etl_name)
        return blood_dag(request, etl.id)
    except ObjectDoesNotExist:
        message = u'%s 不存在' % etl_name
        return render(request, 'common/message.html', {'message': message})


def his(request, tblName):
    etls = ETL.objects.filter(name=tblName).order_by('-ctime')
    return render(request, 'etl/his.html', {'etls': etls, 'tblName': tblName})


def add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                etl = ETL()
                httputils.post2obj(etl, request.POST, 'id')
                userutils.add_current_creator(etl, request)
                find_ = etl.name.find('@')
                etl.meta = etl.name[0: find_]
                etl.save()
                logger.info('ETL has been created successfully : %s ' % etl)
                deps = hivecli.getTbls(etl)
                for dep in deps:
                    if etl.name != dep:
                        tblBlood = TblBlood(tblName=etl.name, parentTbl=dep, relatedEtlId=etl.id)
                        tblBlood.save()
                        logger.info('Tblblood has been created successfully : %s' % tblBlood)
                return HttpResponseRedirect(reverse('metamap:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        return render(request, 'etl/edit.html')


def edit(request, pk):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                privious_etl = ETL.objects.get(pk=int(pk))
                privious_etl.valid = 0
                privious_etl.save()

                deleted, rows = TblBlood.objects.filter(relatedEtlId=pk).delete()
                logger.info('Tblbloods for %s has been deleted successfully' % (pk))

                if int(request.POST['valid']) == 1:
                    etl = privious_etl
                    privious_etl.id = None
                    privious_etl.ctime = timezone.now()
                    httputils.post2obj(etl, request.POST, 'id')
                    userutils.add_current_creator(etl, request)
                    find_ = etl.name.find('@')
                    etl.meta = etl.name[0: find_]

                    etl.save()
                    logger.info('ETL has been created successfully : %s ' % etl)

                    tasks = WillDependencyTask.objects.filter(rel_id=pk, type=1)
                    for task in tasks:
                        task.rel_id = etl.id
                        task.save()

                    logger.info('WillDependencyTask for %s has been deleted successfully' % (pk))

                    deps = hivecli.getTbls(etl)
                    for dep in deps:
                        logger.info("dep is %s, tblName is %s " % (dep, etl.name))
                        if etl.name != dep:
                            tblBlood = TblBlood(tblName=etl.name, parentTbl=dep, relatedEtlId=etl.id)
                            tblBlood.save()
                            logger.info('Tblblood has been created successfully : %s' % tblBlood)
                    logger.info('Tblblood for %s has been created successfully' % (pk))
                return HttpResponseRedirect(reverse('metamap:index'))
        except Exception, e:
            return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    else:
        etl = ETL.objects.get(pk=pk)
        return render(request, 'etl/edit.html', {'etl': etl})


def exec_job(request, etlid):
    etl = ETL.objects.get(id=etlid)
    location = AZKABAN_SCRIPT_LOCATION + dateutils.now_datetime() + '-' + etl.name.replace('@', '__') + '.hql'
    etlhelper.generate_etl_file(etl, location)
    log_location = location.replace('hql', 'log')
    with open(log_location, 'a') as log:
        with open(location, 'r') as hql:
            log.write(hql.read())
    # work_manager.add_job(threadpool.do_job, 'hive -f ' + location, log_location)
    # logger.info(
    #     'job for %s has been executed, current pool size is %d' % (etl.name, work_manager.work_queue.qsize()))
    execution = Executions(logLocation=log_location, job_id=etlid, status=0)
    execution.save()
    from metamap import tasks
    tasks.exec_etl.delay('hive -f ' + location, log_location)
    return redirect('metamap:execlog', execid=execution.id)
    # return redirect('metamap:execlog', execid=1)


def review_sql(request, etlid):
    try:
        etl = ETL.objects.get(id=etlid)
        hql = etlhelper.generate_etl_sql(etl)
        # return render(request, 'etl/review_sql.html', {'obj': etl, 'hql': hql})
        return HttpResponse(hql.replace('\n', '<br>'))
    except Exception, e:
        logger.error(e)
        return HttpResponse(e)


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'etl/exec_log.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = Executions.objects.get(pk=execid)
    with open(execution.logLocation, 'r') as log:
        content = log.read().replace('\n', '<br>')
    return HttpResponse(content)


class ExecLogView(generic.ListView):
    '''
    返回指定job的所有执行记录
    :param jobid:
    :return:
    '''
    template_name = 'etl/executions.html'
    context_object_name = 'executions'
    model = Executions
    paginate_by = DEFAULT_PAGE_SIEZE

    def get_queryset(self):
        jobid_ = self.kwargs['jobid']
        return Executions.objects.filter(job_id=jobid_).order_by('-start_time')


def preview_job_dag(request):
    try:
        bloods = TblBlood.objects.filter(valid=1).all()
        return render(request, 'etl/blood.html', {'bloods': bloods})
    except Exception, e:
        logger.error('error : %s ' % e)
        return HttpResponse('error')


def send_email(request):
    subject = request.POST.get('subject', 'willtest')
    message = request.POST.get('message', 'willtest')
    from_email = request.POST.get('from_email', 'yinkerconfluence@yinker.com')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ['chenxin@yinker.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse('Ok header found.')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')


def send_email2(request):
    subject = request.POST.get('subject', 'willtest')
    message = request.POST.get('message', 'willtest')
    from_email = request.POST.get('from_email', 'yinkerconfluence@yinker.com')
    if subject and message and from_email:
        try:
            email = EmailMessage(
                u'中文题目',
                u'中文内容',
                'yinkerconfluence@yinker.com',
                ['chenxin@yinker.com'],
                ['xuexu@yinker.com'],
            )
            email.attach_file(u'/root/月度目标数据-20170210095000')

            email.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse('Ok header found.')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')


def filedownload(request):
    user = request.GET['user']
    sid = request.GET['sid']
    filename = request.GET['filename']
    result = httputils.jlc_auth(user, sid)
    if result == 'success':
        full_file = constants.TMP_EXPORT_FILE_LOCATION + filename
        if result == 'success':
            response = FileResponse(open(full_file, 'rb'))
        response['Content-Disposition'] = 'attachment; filename=te.sh'
        return response
    else:
        return HttpResponse("session is not valid")


def restart_job(request):
    '''
    指定调度周期与etl名字
    抽取所有指定etlid子节点的有效的ETL, 生成azkaban调度文件
    :param request:
    :return:
    '''
    if request.user.username == 'admin':
        if request.method == 'POST':
            try:
                final_bloods = set()
                dependencies = {}
                schedule = int(request.POST.get('schedule'))

                for name in request.POST.get('names').split(','):
                    dependencies[name] = set()
                    for blood in TblBlood.objects.filter(tblName=name):
                        bloodhelper.find_child_mermaid(blood, final_bloods)

                for blood in final_bloods:
                    child_name = blood.tblName
                    c_etl = ETL.objects.get(name=child_name, valid=1)
                    if WillDependencyTask.objects.filter(rel_id=c_etl.id, schedule=schedule, type=1).exists():
                        dependencies.setdefault(child_name, set())
                        parent_name = blood.parentTbl
                        p_etl = ETL.objects.get(name=parent_name, valid=1)
                        if WillDependencyTask.objects.filter(rel_id=p_etl.id, schedule=schedule, type=1).exists():
                            dependencies.get(child_name).add(parent_name)

                folder = 'h2h-' + dateutils.now_datetime() + '-restart'
                os.mkdir(AZKABAN_BASE_LOCATION + folder)
                os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

                for job_name, parent_names in dependencies.items():
                    etlhelper.generate_job_file_for_partition(job_name, parent_names, folder, schedule)
                etlhelper.generate_job_file_for_partition('etl_done_' + folder, dependencies.keys(), folder)
                ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
                return HttpResponse(folder)
            except Exception, e:
                logger.error('error : %s ' % e)
                logger.error('traceback is : %s ' % traceback.format_exc())
                return HttpResponse('error')
        else:
            return render(request, 'etl/restart.html')
    else:
        return HttpResponse('no auth')

def generate_job_dag(request, schedule):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        done_blood = set()
        done_leaf = set()
        folder = 'h2h-' + dateutils.now_datetime()
        leafs = TblBlood.objects.raw("select a.* from "
                                     + "(select * from metamap_tblblood where valid = 1) a"
                                     + " join "
                                     + " (select rel_id from metamap_willdependencytask where schedule=" + schedule + " and valid=1 and type = 1) s "
                                     + " on s.rel_id = a.related_etl_id"
                                     + " left outer join "
                                     + "(select distinct parent_tbl from metamap_tblblood where valid = 1) b"
                                     + " on a.tbl_name = b.parent_tbl"
                                     + " where b.parent_tbl is null")
        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.load_nodes(leafs, folder, done_blood, done_leaf, schedule)
        tbl = TblBlood(tblName='etl_done_' + folder)
        etlhelper.generate_job_file(tbl, leafs, folder)
        PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE),
                                   '%d etls generated ' % len(done_blood))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')


def generate_job_dag_v2(request, schedule):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        done_blood = set()
        done_leaf = set()
        folder = 'generate_job_dag_v2-' + dateutils.now_datetime()
        leafs = ETLBlood.objects.raw("SELECT 1 as id, a.* FROM "
                                      "(select DISTINCT child_id FROM metamap_etlblood) a "
                                     "join ("
                                        "select rel_id from metamap_willdependencytask where `schedule` = " + schedule +" and valid=1 and type = 100 "
                                        ") b "
                                            "on a.child_id = b.rel_id "
                                     "left outer join ("
                                     "SELECT DISTINCT parent_id from metamap_etlblood ) c "
                                        "on a.child_id = c.parent_id "
                                    "where c.parent_id is NULL")

        final_deps = set()
        leaves = set()
        for leaf in leafs:
            leaf_bloods = ETLObj.objects.get(pk=leaf.child_id)
            final_deps.add(leaf_bloods.name)
            leaves.add(leaf_bloods.id)

        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.load_nodes_v2(leaves, folder, done_blood, done_leaf, schedule)

        etlhelper.generate_job_file_v2(ETLObj(name='etl_done_' + folder), final_deps, folder, folder)
        # PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE),
        #                            '%d etls generated ' % len(done_blood))
        # ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')