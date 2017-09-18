import traceback

import time
from django.test import TestCase
from django.utils import timezone
from marathon import MarathonHttpError
from marathon import NotFoundError

from running_alert import tasks
from running_alert.models import MonitorInstance, SparkMonitorInstance
from running_alert.utils import consts
from running_alert.utils.consts import REDIS_KEY_JMX_CHECK_LAST_ADD_TIME
from will_common.utils import redisutils


class MonitorTestCase(TestCase):
    def test_jmx(self):
        MonitorInstance.objects.create(host_and_port='10.1.5.190:3432', instance_name='test',
                                       service_type='kafka')
        obj = MonitorInstance.objects.get(instance_name='test')
        self.assertEqual(obj.host_and_port, '10.1.5.190:3432')


        # filter the newest monitor instance

    def test_spark(self):
        now_time = timezone.now()
        time.sleep(3)
        obj = SparkMonitorInstance.objects.create(instance_name='test_spark')
        print(str(now_time))

        result = SparkMonitorInstance.objects.filter(utime__gt=str(now_time))
        print(str(obj.utime))
        self.assertEqual(len(result), 1)

    def test_check_add_jmx(self):
        try:
            ll = redisutils.get_val(REDIS_KEY_JMX_CHECK_LAST_ADD_TIME)
            tasks.check_new_inst()
            self.assertTrue(ll < redisutils.get_val(REDIS_KEY_JMX_CHECK_LAST_ADD_TIME))
            print('got prometheus avaliable port {port}'.format(port=tasks.get_avaliable_port()))
        except:
            print traceback.format_exc()
