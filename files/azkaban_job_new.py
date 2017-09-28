#!/usr/bin/python
#coding:utf-8
user = 'azkaban'
pwd = '15yinker@bj'
host = 'http://10.2.19.62:8081'
metamap_host='10.2.19.62:8888'
import urllib2,json, urllib


import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--group',dest='group', 
                    action='store',
                    default='jlc',
                    help='specify the target schedule group: jlc, xiaov')
parser.add_argument('--jobtype',dest='jobtype',  
                    action='store',
                    default='etls',
                    help='specify the target jobtype: m2h, etls, h2m')
parser.add_argument('--schedule',dest='schedule',  
                    action='store',
	            type=int,
                    default=0,
                    help='specify the target schedule type: 0(day), 1(week), 2(month)')
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


def generate_task_files(jobtype, schedule, group):
    target = 'http://10.2.19.62:8888/metamap/{job_type}/generate_job_dag/{num}/{group_name}/'.format(job_type=job_type, num=schedule, group_name=group)
    resp = requests.get(target)
    zip_file = '/tmp/{filename}.zip'.format(filename=resp.content)
    print('Got job file %s' % zip_file)
    return zip_file

    
def go_schedule(project, target_file):
    from azkaban import *
    fetcher = CookiesFetcher(user, pwd)
    project = Project('WillTest', 'first test', fetcher)
    project.create_prj()
    project.upload_zip('/tmp/h2h-20170923030038.zip')
    for flow in project.fetch_flow():
        execution = flow.execute()
        execution.handle_timeout()
    print('all end for %s ....' % project)


generate_task_files(args.jobtype, args.schedule, args.group)
