from django.core.management import BaseCommand

from metamap.models import SqoopMysql2Hive


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # parser.add_argument(
        #     '--old_name',
        #     action='store',
        #     dest='old_name',
        #     default='noname',
        #     help='Delete poll instead of closing it',
        # )
        # parser.add_argument(
        #     '--new_name',
        #     action='store',
        #     dest='new_name',
        #     default='noname',
        #     help='Delete poll instead of closing it',
        # )
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

        for etl in SqoopMysql2Hive.objects.filter(cgroup__name=options['group'], name__startswith='import_wb_xiaodai'):
            try:
                etl.id = None
                etl.name = etl.name.replace('wb', 'univ')
                etl.option = etl.option.replace('wb', 'univ')
                etl.mysql_meta_id = 58
                etl.hive_meta_id = 60
                etl.columns = etl.columns + ',CHANNEL'
                etl.save()
            except Exception, e:
                print('SqoopMysql2Hive \'s error : %d --> %s' % (etl.id, e))
        self.stdout.write(self.style.SUCCESS('Successfully "%s"' % 'will'))
