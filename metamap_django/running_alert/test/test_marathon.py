import traceback
import unittest
from unittest import TestCase

from marathon import MarathonClient
from marathon import MarathonHttpError
from marathon import NotFoundError


class MarathonTestCase(TestCase):
    def setUp(self):
        self.c = MarathonClient('http://10.1.5.190:8080')

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        for a in self.c.list_apps():
            print a

    def test_del_app(self):
        try:
            print self.c.delete_app('sparkjsonexporter2')
        except NotFoundError, e:
            print traceback.format_exc()
            print('NotFoundError--->' + e.message)
        except MarathonHttpError, e:
            print traceback.format_exc()
            print('MarathonHttpError---->' + e.message)
        print('Haha')


    def test_get_app(self):
        rr =  self.c.list_apps()
        print rr
        new_app = self.c.get_app('flume10219635445')
        task = new_app.tasks[0]
        host_port = task.ports[0]
        host = task.host
        print host, host_port

if __name__ == '__main__':
    c = MarathonClient('http://10.1.15.190:8080')
    new_app = c.get_app('flume10219635445')
    host_port = new_app.tasks[0].ports[0]