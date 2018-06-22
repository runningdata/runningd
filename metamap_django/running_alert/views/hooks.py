# !/usr/bin/env python
# -*- coding: utf-8 -*
import json
import traceback

from django.conf import settings
from django.http import HttpResponse
from running_alert.models import MonitorInstance, SparkMonitorInstance
from will_common.models import UserProfile
from will_common.utils import PushUtils
from will_common.utils.encryptutils import decrpt_msg


def alert_for_prome(request):
    if request.method == 'POST':
        try:
            message = json.loads(request.body)
            summary = message['commonAnnotations']['summary']
            description = message['commonAnnotations']['description']
            alertname = message['commonLabels']['alertname']
            app_name = message['commonLabels']['app_name']
            if 'spark' not in message['commonLabels']['service']:
                obj = MonitorInstance.objects.get(host_and_port=message['commonLabels']['host_and_port'])
            else:
                obj = SparkMonitorInstance.objects.get(instance_name=message['commonLabels']['app_name'])
            target_users = []
            for manager in obj.managers.split(','):
                target_users.append(UserProfile.objects.get(user__username=manager))

            p_msg = u'告警名称： %s.%s\n 标题: %s. 描述: %s' % (
                app_name, alertname, summary, description)
            if 'absent' not in message['commonLabels']:
                PushUtils.push_msg(target_users, p_msg)

            PushUtils.push_msg_tophone(decrpt_msg(settings.ADMIN_PHONE), p_msg)
            PushUtils.push_wechat_touser('admin', p_msg)
            return HttpResponse('Done')
        except Exception, e:
            print traceback.format_exc()
            print message
    else:
        return HttpResponse('use POST please')
