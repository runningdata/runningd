# -*- coding: utf-8 -*
import json
import os
import subprocess

import re

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

import metamap
from metamap import tasks
from will_common.models import OrgGroup, UserProfile
from will_common.utils import PushUtils
from will_common.utils import constants
from will_common.utils import dateutils
from will_common.utils import redisutils
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION, TMP_EXPORT_FILE_LOCATION

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
    # {u'will_dqms@schedule.yinker.com': [],
    #  u'will_jar@schedule.yinker.com': [{u'acknowledged': True,
    #                                     u'args': u"(u'java -cp /server/metamap/metamap_django/jars/xmark_supervise_gettest-1.0-SNAPSHOT.jar -Dtest.user.name=chenxin HTTPGEt \\u53c2\\u65701 \\u53c2\\u65702  2017-05-04', 1865L)",
    #                                     u'delivery_info': {u'exchange': u'running_jar',
    #                                                        u'priority': 0,
    #                                                        u'redelivered': None,
    #                                                        u'routing_key': u'running_jar'},
    #                                     u'hostname': u'will_jar@schedule.yinker.com',
    #                                     u'id': u'ac6cc44e-c184-45fc-82e5-3f56cf5c69bf',
    #                                     u'kwargs': u'{}',
    #                                     u'name': u'metamap.tasks.exec_jar',
    #                                     u'time_start': 1349955.30187257,
    #                                     u'worker_pid': 21114}],
    #  u'will_metamap@schedule.yinker.com': []}
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
    PushUtils.push_both(users, ' project %s : status : %s' % (prjname, status))
    return HttpResponse('done')


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
        current_datee = ''
        for line in dfs_log.readlines():
            if line.startswith('new'):
                datee = line.split(' ')[2].replace('\n', '')
                if datee == dateutils.now_datekey():
                    current_datee = datee
            else:
                size = pattern.split(line)[0]
                ssize = float(size.split(' ')[0])
                if pattern.split(line)[1] == 'G':
                    ssize = ssize * 1024
                db = pattern.split(line)[2].replace('/', '_').replace('\n', '').replace('_apps_hive_warehouse_', '')
                if len(db) < 1:
                    continue
                result[db] = ssize
    return render(request, 'ops/dfs_now.html', {"result": result, })
