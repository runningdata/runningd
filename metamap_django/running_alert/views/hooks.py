import json
import traceback

from django.http import HttpResponse
from running_alert.models import MonitorInstance, SparkMonitorInstance
from will_common.models import UserProfile
from will_common.utils import PushUtils


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

            p_msg = 'Alert for %s.%s. summary is : %s. description is : %s' % (
                app_name, alertname, summary, description)
            PushUtils.push_msg(target_users, p_msg)

            PushUtils.push_msg_tophone('15210976096', p_msg)
            return HttpResponse('Done')
        except Exception, e:
            print traceback.format_exc()
            print message
    else:
        return HttpResponse('use POST please')
