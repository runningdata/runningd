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
parser.add_argument('--execid',dest='execid',
                    action='store',
                    type=int,
                    default=0,
                    help='execution id')
parser.add_argument('--flowid',dest='flowid',
                    action='store',
                    help='the flow id')
parser.add_argument('--prjname',dest='prjname',
                    action='store',
                    help=u'project name')
args = parser.parse_args()
fetcher = CookiesFetcher(user, pwd)
execution = FlowExecution(args.prjname, args.flowid, args.execid, fetcher)
execution.handle_timeout()
