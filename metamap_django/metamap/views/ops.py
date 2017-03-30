# -*- coding: utf-8 -*
import os
import subprocess

from django.contrib.auth.models import Group
from django.http import HttpResponse
import logging

from django.shortcuts import render

from metamap.models import Exports
from will_common.utils import dateutils
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION

logger = logging.getLogger('django')


def tail_hdfs(request):
    dfs_path = request.GET['dfs_path']
    line_num = request.GET['line_num']
    if 'sid' in request.GET:
        sid = request.GET['sid']

    user = request.user
    group = Group.objects.get(user=user)
    filename = 'tailhdfs-' + user.username + dateutils.now_datetime()
    logLocation = AZKABAN_SCRIPT_LOCATION + filename
    cmd = 'hdfs dfs -cat %s/* | tail -n %s' % (dfs_path, line_num)
    command = 'runuser -l ' + group.name + ' -c "' + cmd + '"'
    with open(logLocation, 'a') as fi:
        p = subprocess.Popen([''.join(command)], stdout=fi, stderr=subprocess.STDOUT,
                             shell=True,
                             universal_newlines=True)
        p.wait()
        returncode = p.returncode
    logger.info('tail_hdfs : %s return code is %d' % (command, returncode))
    # content = 'sth happend, please info the manager'
    # with open(logLocation, 'r') as tt:
    #     content = tt.read()
    # return HttpResponse(content)
    return render(request, 'ops.html', {'user': request.user.username,
                                        'filename': filename,
                                        'group': group.name
                                        })
