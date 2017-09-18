import traceback

from django.test import TestCase
from marathon import MarathonHttpError
from marathon import NotFoundError

from running_alert import tasks


class MarathonTestCase(TestCase):
    def setUp(self):
        self.c = tasks.c

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
