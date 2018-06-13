# -*- coding: utf-8 -*
user = ''
pwd = '@bj'
old_azkaban = 'http://10.103.70.27:2226'
new_azkaban = 'http://azkaban.data.p.tp'

from azkaban_client.azkaban import *


def go_transfer(proj_name):
    old_fetcher = CookiesFetcher(old_azkaban, user, pwd)
    new_fetcher = CookiesFetcher(new_azkaban, user, pwd)

    print 'fetcher done'
    old_project = Project(old_azkaban, proj_name, 'first test', old_fetcher)
    azkaban_job_file = '/tmp/%s.zip' % proj_name
    old_project.download(azkaban_job_file)
    print('downloaded down for %s ' % azkaban_job_file)
    new_project = Project(new_azkaban, proj_name, 'first test', new_fetcher)
    new_project.create_prj()
    new_project.upload_zip(azkaban_job_file)
    for flow in new_project.fetch_flow():
        print flow
        execution = flow.execute()
        execution.handle_timeout()
    print('all end for %s ....' % proj_name)

fetcher = CookiesFetcher(new_azkaban, user, pwd)
execution = FlowExecution(new_azkaban, 'h2h-20180601031821', 'etl_done_jlc_h2h-20180601031821', '34643', fetcher)
execution.handle_timeout()
with open('/root/gitLearning/metamap/files/all_project') as todo_p:
    for line in todo_p.readlines():
        go_transfer(line.strip())
