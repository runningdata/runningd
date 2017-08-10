#!/usr/bin/python
#coding:utf-8
user = 'azkaban'
pwd = '15yinker@bj'
host = 'http://10.2.19.62:8081'
import urllib2,json, urllib


import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--execid',dest='execid', 
		    action='store',
                    default='noexecid',
                    help='support execid for action')
parser.add_argument('--cancel',dest='cancel',
		    type=bool,
                    action='store',
                    default=True,
                    help='going to cancel a flow if it has been reached timeout?')
parser.add_argument('--flow_timeout',dest='flow_timeout',
                    type=int,
                    action='store',
                    default=210,
                    help=u'单flow超时时间')
args = parser.parse_args()

data = {'username': user, 'password': pwd, 'action': 'login'}
# get SESSION ID
request = urllib2.Request(host, data=urllib.urlencode(data))
contents = urllib2.urlopen(request).read()
session=json.loads(contents)['session.id']

def do_kill():
    if args.cancel and args.execid:
        # kill target execid
        target= '%s/executor?ajax=cancelFlow&session.id=%s&execid=%s' % (host, session, args.execid)
        request = urllib2.Request(target)
        resp = urllib2.urlopen(request)
        if resp.getcode() != 200:
	    print(resp.read() + '\n')

import time
def get_current_timekey():
    return time.strftime("%Y%m%d%H%M%S")



job_status_dict = dict()

# 获取flow的执行信息
def get_flow_info(exec_id, job_status_dict):
    target= '%s/executor?ajax=fetchexecflow&session.id=%s&execid=%s' % (host, session, args.execid)
    request = urllib2.Request(target)
    contents = urllib2.urlopen(request).read()
    result=json.loads(contents)
    start_time = result['startTime']
    start_time = start_time /1000
    for dd in result['nodes']:
	cu = job_status_dict.get(dd['status'], set())
	cu.add(dd['id'])
	job_status_dict[dd['status']] = cu
    for k, v in job_status_dict.items():
        print('%s  status: %s : %d/%d \n' % (get_current_timekey(), k, len(v), len(result['nodes'])))   
    if int(time.time()) - start_time > 60 * args.flow_timeout and result['endTime'] == -1:
	print('reached timeout threshold \n')
	do_kill()
	time.sleep(60)
        resume_flow(result['project'], result['flow'])	
    else:
        print('i10d %s \n' % args.execid)
    print('r10r %s \n' % result['status'])


def get_str_set(xx):
    union_set = job_status_dict.get('SUCCEEDED', set()).union(job_status_dict.get('SKIPPED', set()))
    return "[\"" + "\",\"".join(union_set) + "\"]"

# 重新启动某个flow的调用
def resume_flow(project, flow):
    target= '%s/executor?ajax=executeFlow&session.id=%s&project=%s&flow=%s&disabled=%s' % (host, session, project,flow, get_str_set(job_status_dict.get('SUCCEEDED', set())))
    #handler=urllib2.HTTPHandler(debuglevel=1)
    handler=urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request(target)
    contents = urllib2.urlopen(request).read()
    print('i10d %s \n' % json.loads(contents)['execid'])

get_flow_info(args.execid, job_status_dict)
