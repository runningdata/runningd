# -*- coding: utf-8 -*
import json
import os
import subprocess

import re

import celery
from celery.backends import redis
from django.contrib.auth.models import Group
from django.http import HttpResponse
import logging

from django.shortcuts import render

import metamap
from metamap import tasks
from metamap.models import Exports
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
    # i = metamap.celery.app.control.inspect()
    # print i.active_queues()
    final_queue = dict()
    str = list()
    for queue_key in redisutils.get_keys():
        print queue_key
        final_queue[queue_key] = redisutils.get_queue_count(queue_key)
        str.append('<%s> : %d tasks waiting' % (queue_key, final_queue[queue_key]))
    result = ' | '.join(str)
    return render(request, 'ops/task_queue.html', {"final_queue": final_queue, "str": result})


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
