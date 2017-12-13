# -*- coding: utf-8 -*
import json
import os
import subprocess

import re

import time
import traceback

from django import forms
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

import metamap
from metamap import tasks
from metamap.models import Exports, ExecObj, AnaETL, Executions, ExecutionsV2
from will_common.models import OrgGroup, UserProfile, WillDependencyTask
from will_common.utils import PushUtils
from will_common.utils import constants
from will_common.utils import dateutils
from will_common.utils import redisutils
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION, TMP_EXPORT_FILE_LOCATION, DEFAULT_PAGE_SIEZE
from will_common.utils.customexceptions import RDException

logger = logging.getLogger('django')


def tail_hdfs(request):
    dfs_path = request.GET['dfs_path']
    line_num = request.GET['line_num']
    if 'sid' in request.GET:
        sid = request.GET['sid']

    user = request.user
    group = Group.objects.get(user=user)
    filename = 'tailhdfs-' + user.username + dateutils.now_datetime()
    logLocation = TMP_EXPORT_FILE_LOCATION + filename
    cmd = 'hdfs dfs -cat %s/* | tail -n %s' % (dfs_path, line_num)
    command = 'runuser -l ' + group.name + ' -c "' + cmd + '"'
    # msg = '<a href="http://10.1.5.83:8000/metamap/rest/exports/get_file?filename=%s&user=%s&group=%s&sid=sid">%s点击下载</a>' \
    #       % (filename, request.user.username, group.name, filename)
    tasks.tail_hdfs.delay(logLocation, command)
    # content = 'sth happend, please info the manager'
    # with open(logLocation, 'r') as tt:
    #     content = tt.read()
    # return HttpResponse(content)
    return render(request, 'ops/hdfs_proc.html', {'username': request.user.username,
                                                  'filename': filename + '_done',
                                                  'groupname': group.name
                                                  })


def check_file(request):
    filename = request.GET['filename']
    logLocation = TMP_EXPORT_FILE_LOCATION + filename
    if os.path.exists(logLocation):
        return HttpResponse("success")
    return HttpResponse("not yet")


def task_queue(request):
    i = metamap.celery.app.control.inspect()
    running = i.active()
    final_queue = dict()
    str = list()
    for queue_key in redisutils.get_keys():
        print queue_key
        final_queue[queue_key] = redisutils.get_list(queue_key)
        str.append('<%s> : %d tasks waiting' % (queue_key, len(final_queue[queue_key])))
    result = ' | '.join(str)

    unacked = redisutils.get_dict('unacked')
    return render(request, 'ops/task_queue.html',
                  {"final_queue": final_queue, "str": result, "running": running, "unack": unacked})


def dfs_usage_his(request):
    if 'search' in request.GET and '*' != request.GET['search']:
        db_pattern = re.compile(r'.*' + request.GET['search'] + '.*')
    else:
        db_pattern = re.compile(r'.*')
    pattern = re.compile(r'\s+')
    final = dict()
    dateee = set()
    with open('/tmp/dfs-usage-snapshot_bb.log') as dfs_log:
        current_datee = ''
        for line in dfs_log.readlines():
            if line.startswith('new'):
                datee = line.split(' ')[2].replace('\n', '')
                current_datee = datee
                if current_datee > dateutils.days_ago_key(-30):
                    dateee.add(current_datee)
            else:
                size = pattern.split(line)[0]
                ssize = float(size.split(' ')[0])
                if pattern.split(line)[1] == 'G':
                    ssize = ssize * 1024
                db = pattern.split(line)[2].replace('/', '_').replace('\n', '').replace('_apps_hive_warehouse_', '')
                if not db_pattern.match(db):
                    continue
                if len(db) < 1:
                    continue
                if db not in final:
                    final[db] = dict()
                final[db][current_datee] = ssize
    l = list(dateee)
    l.sort()
    return render(request, 'ops/hdfs_his.html', {"dateee": l, "dbs": final.keys(), "finall": final})


def push_msg(request):
    group = request.GET['group']
    prjname = request.GET['prjname']
    status = request.GET['status']
    owners = OrgGroup.objects.get(name=group).owners
    users = set()
    for owner in owners.split(','):
        users.add(UserProfile.objects.get(user__username=owner))
    users.add(UserProfile.objects.get(user__username='admin'))
    PushUtils.push_both(users, ' project %s : status : %s' % (prjname, status))
    return HttpResponse('done')


def push_single_msg(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        msg = request.POST['msg']
        tt = PushUtils.push_msg_tophone(phone, msg)
        return HttpResponse(tt)


def push_single_email(request):
    if request.method == 'POST':
        email = request.POST['email']
        msg = request.POST['msg']
        subject = request.POST['subject']
        tt = PushUtils.push_exact_html_email(email, subject, msg)
        return HttpResponse(tt)


def hdfs_files(request):
    path = '/user/%s' % request.user.username
    command = 'hdfs dfs -ls %s | grep ^[^d] | grep user | awk \'{print substr($8, length("%s") + 1)}\'' % (path, path)
    p = subprocess.Popen([''.join(command)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         shell=True,
                         universal_newlines=True)
    out, err = p.communicate()
    print out
    print err
    return render(request, 'ops/hdfs_list.html', {'objs': [f for f in out.split('\n') if len(f.strip()) > 0]})


def hdfs_del(request, filename):
    if '..' in filename:
        print('error file %s ' % filename)
        return HttpResponseRedirect(reverse('metamap:hdfs_files'))
    path = '/user/%s' % request.user.username + '/' + filename
    command = 'hdfs dfs -rm %s ' % path
    p = subprocess.Popen([''.join(command)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         shell=True,
                         universal_newlines=True)
    out, err = p.communicate()
    print out
    print err
    return HttpResponseRedirect(reverse('metamap:hdfs_files'))


class UploadFileForm(forms.Form):
    file = forms.FileField()


def exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    return render(request, 'executions/exec_log.html', {'execid': execid})


def get_exec_log(request, execid):
    '''
    获取指定execution的log内容
    :param request:
    :param execid:
    :return:
    '''
    execution = ExecutionsV2.objects.get(pk=execid)

    try:
        with open(execution.log_location, 'r') as log:
            content = log.read().replace('\n', '<br>')
    except:
        return HttpResponse('')
    return HttpResponse(content)


class StatusListView(generic.ListView):
    template_name = 'components/common_executions_list.html'
    context_object_name = 'executions'
    url_base = 'url_base'

    def get(self, request, status):
        self.paginate_by = DEFAULT_PAGE_SIEZE
        if request.user.username == 'admin':
            self.object_list = ExecutionsV2.objects.filter(status=status).exclude(job__type=2).order_by('-start_time')
        else:
            self.object_list = ExecutionsV2.objects.filter(status=status,
                                                           job__cgroup=request.user.userprofile.org_group) \
                .exclude(job__type=2).order_by('-start_time')
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Exception("Empty list and '%(class_name)s.allow_empty' is False.")
        context = self.get_context_data()
        context['url_base'] = self.url_base
        return self.render_to_response(context)


def rerun(request):
    if request.method == 'POST':
        str_list = list()
        file_date = request.POST['file_date']
        to_delete = request.POST['is_del']
        for ex in ExecutionsV2.objects.filter(log_location__contains=file_date):
            eo = ex.job
            if eo.type == 2:
                if eo.cgroup == request.user.userprofile.org_group:
                    # TODO if this task is already in queue, then go pass
                    str_list.append('task %s has been rescheduled ' % eo.name)
                    task = WillDependencyTask.objects.get(rel_id=eo.id, type=100)
                    tasks.exec_etl_cli2.delay(task.id, name=eo.name)
                    time.sleep(1)
                    if int(to_delete) == 1:
                        ex.delete()

        return HttpResponse('<br/>'.join(str_list))
    else:

        return render(request, 'hadmin/rerun.html')


def upload_hdfs_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            ff = request.FILES['file']
            # path = default_storage.save('tmp/somename.mp3', ContentFile(ff.read()))
            # tmp_file = os.path.join(constants.TMP_HDFS_FILE_LOCATION, path)
            with default_storage.open('hdfstmp/' + ff.name, 'wb+') as destination:
                for chunk in ff.chunks():
                    destination.write(chunk)

            local = 'hdfstmp/' + ff.name
            path = '/user/%s' % request.user.username + '/'
            command = 'hdfs dfs -put %s %s' % (local, path)
            p = subprocess.Popen([''.join(command)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 shell=True,
                                 universal_newlines=True)
            out, err = p.communicate()
            if p.returncode == 0:
                return HttpResponseRedirect(reverse('metamap:hdfs_files'))
            else:
                print(err)
                return render(request, 'source/post_edit.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'source/post_edit.html', {'form': form})


def dfs_usage(request):
    pattern = re.compile(r'\s+')
    result = dict()
    with open('/tmp/dfs-usage-snapshot_bb.log') as dfs_log:
        got_today = False
        for line in dfs_log.readlines():
            try:
                if line.strip().endswith(dateutils.now_datekey()):
                    datee = line.split(' ')[2].replace('\n', '')
                    got_today = True
                else:
                    if not got_today:
                        continue
                    size = pattern.split(line)[0]
                    ssize = float(size.split(' ')[0])
                    if pattern.split(line)[1] == 'G':
                        ssize = ssize * 1024
                    db = pattern.split(line)[2].replace('/', '_').replace('\n', '').replace('_apps_hive_warehouse_', '')
                    if len(db) < 1:
                        continue
                    result[db] = ssize
            except Exception, e:
                print dateutils.now_datekey()
                print line
                raise RDException(line, traceback.format_exc())
    return render(request, 'ops/dfs_now.html', {"result": result, })
