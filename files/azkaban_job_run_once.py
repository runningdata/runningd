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
parser.add_argument('--cancel',dest='cancel',
                    type=bool,
                    action='store',
                    default=True,
                    help='going to cancel a flow if it has been reached timeout?')
parser.add_argument('--prjname',dest='prjname',
                    action='store',
                    help=u'project name.')
args = parser.parse_args()
try:
    fetcher = CookiesFetcher(user, pwd)
    project = Project(args.prjname, 'desc for once', fetcher)
    for flow in project.fetch_flow():
        execution = flow.execute()
        execution.handle_timeout()
    print('all end for %s....' % project.name)
except Exception, e:
    print e.message
    create_data = {
        'msg':'Error happended for daily schedule %s ' % e.message,
        'phone': conf['ADMIN_PHONE']
    }
    r = requests.post('http://%s/nosecure/ops/push_single_msg/' % metamap_host, data=create_data)
    print r.text

 
