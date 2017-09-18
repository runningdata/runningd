from django.core.management import BaseCommand

user = 'azkaban'
pwd = '15yinker@bj'
host = 'http://10.2.19.62:8081'


class Command(BaseCommand):
    help = 'xx'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job_type',
            action='store',
            dest='job_type',
            default='noname',
            help='Delete poll instead of closing it',
        )
        parser.add_argument(
            '--flow_id',
            action='store',
            dest='flow_id',
            default='noname',
            help='Delete poll instead of closing it',
        )
        parser.add_argument(
            '--group',
            action='store',
            dest='group',
            default='noname',
            help='Delete poll instead of closing it',
        )
        # parser.add_argument("--keyvalue", action='append',
        #                type=lambda kv: kv.split("="), dest='keyvalues')

    def handle(self, *args, **options):
        for arg in args:
            self.stdout.write('I got arg : %s ' % arg)

        for k, v in options.iteritems():
            self.stdout.write('I got kv : %s , %s ' % (k, v))

        import urllib2
        data = {'username': user, 'password': pwd, 'action': 'login'}

        request = urllib2.Request("http://thewebsite.com", data=data)
        contents = urllib2.urlopen(request).read()
        print contents

        self.stdout.write(self.style.SUCCESS('Successfully "%s"' % 'will'))
