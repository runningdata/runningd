# -*- coding: utf-8 -*
import json
with open('/etc/runningd_schedule.conf') as f:
    conf = json.loads(f.read())
    print conf


user = conf['AZKABAN_USER']
pwd = conf['AZKABAN_PWD']
host = conf['AZKABAN_URL']
metamap_host= conf['RUNNINGD_HOST']
import urllib2,json, urllib

from azkaban_client.azkaban import *

import argparse, requests

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--projname',dest='prj_name',  
                    action='store',
                    help='specify the target projname')
parser.add_argument('--flow_timeout',dest='flow_timeout',
                    type=int,
                    action='store',
                    default=210,
                    help=u'timeout for a flow')
parser.add_argument('--create_file',dest='create_file',
                    action='store',
                    default='yes',
                    help='specify the target projname zip filename')
args = parser.parse_args()


def go_schedule(proj_name, target_file):
    fetcher = CookiesFetcher(user, pwd)
    print 'fetcher done'
    project = Project(proj_name, 'first test', fetcher)
    print project
    if target_file == 'yes':
        project.create_prj()
        project.upload_zip('/tmp/{filename}.zip'.format(filename=proj_name))
    for flow in project.fetch_flow():
        print flow
        execution = flow.execute()
        execution.handle_timeout()
    print('all end for %s ....' % project.name)

print args
try:
    print args.prj_name
    go_schedule(args.prj_name, args.create_file)
except Exception, e:
    import traceback
    print traceback.print_exc()
    create_data = {
            'msg': 'Error happened for daily schedule %s ' % e.message,
            'phone': conf['ADMIN_PHONE']
        }
    r = requests.post('http://%s/nosecure/ops/push_single_msg/' % metamap_host, data=create_data)
    print r.text
