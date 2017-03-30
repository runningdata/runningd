# -*- coding: utf-8 -*
import os
import subprocess

from django.contrib.auth.models import Group
from django.http import HttpResponse
import logging

from django.shortcuts import render

from metamap import tasks
from metamap.models import Exports
from will_common.utils import dateutils
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
                                                  'filename': filename,
                                                  'groupname': group.name
                                                  })


def tail_file(request):
    filename = request.GET['filename']
    logLocation = TMP_EXPORT_FILE_LOCATION + filename
    if os.path.exists(logLocation):
        return HttpResponse("success", mimetype="application/json")
    return HttpResponse("not yet", mimetype="application/json")
