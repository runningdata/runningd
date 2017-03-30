# -*- coding: utf-8 -*
import os
import subprocess

from django.contrib.auth.models import Group
from django.http import HttpResponse
import logging

from will_common.utils import dateutils
from will_common.utils.constants import AZKABAN_SCRIPT_LOCATION

logger = logging.getLogger('django')


def tail_hdfs(request):
    dfs_path = request.GET['dfs_path']
    line_num = request.GET['line_num']
    user = request.user
    group = Group.objects.get(user=user)
    logLocation = AZKABAN_SCRIPT_LOCATION + 'tailhdfs-' + user.username + dateutils.now_datetime()
    cmd = 'hdfs dfs -cat %s/* | tail -n %s' % (dfs_path, line_num)
    command = 'runuser -l ' + group.name + ' -c "' + cmd + '"'
    with open(logLocation, 'a') as fi:
        p = subprocess.Popen([''.join(command)], stdout=fi, stderr=subprocess.STDOUT,
                             shell=True,
                             universal_newlines=True)
        p.wait()
        returncode = p.returncode
    logger.info('tail_hdfs : %s return code is %d' % (command, returncode))
    content = 'sth happend, please info the manager'
    with open(logLocation, 'r') as tt:
        content = tt.read()
    os.remove(logLocation)
    return HttpResponse(content)
