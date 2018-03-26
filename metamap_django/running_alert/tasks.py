# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import json
import os
import random
import traceback

import time

import django
import requests
import subprocess
from celery import shared_task
#
from celery.utils.log import get_task_logger
from django.conf import settings
from marathon import MarathonApp
from marathon import MarathonClient
from marathon import MarathonConstraint
from marathon import MarathonHttpError
from marathon.models import MarathonHealthCheck
from marathon.models.container import MarathonContainer, MarathonDockerContainer, MarathonContainerPortMapping

from running_alert.models import MonitorInstance, SparkMonitorInstance
from running_alert.utils import prometheusutils
from running_alert.utils.consts import *
from will_common.utils import PushUtils
from will_common.utils import httputils
from will_common.utils import redisutils

logger = get_task_logger('running_alert')
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/running_alert/'

c = MarathonClient('http://10.2.19.124:8080')

CONTAINER_PORT = 1234
prometheus_container = 'my-prometheus'


@shared_task(queue='running_alert')
def check_new_jmx(name='check_new_jmx'):
    try:
        last_run = redisutils.get_val(REDIS_KEY_JMX_CHECK_LAST_ADD_TIME)
        print('last run is {ll} for {redis_key}'.format(ll=last_run, redis_key=REDIS_KEY_JMX_CHECK_LAST_ADD_TIME))
        insts = MonitorInstance.objects.filter(utime__gt=last_run, valid=1)
        reset_last_run_time(REDIS_KEY_JMX_CHECK_LAST_ADD_TIME)
        if len(insts) > 0:
            running_ids = [app.id for app in c.list_apps()]
        else:
            return
        need_restart = False
        print insts
        print running_ids
        for inst in insts:
            try:
                tmp_id = get_jmx_app_id(inst)
                service_port = 0
                print('handling jmx {tmp_id}'.format(tmp_id=tmp_id))
                if tmp_id not in running_ids:
                    '''
                    run the docker container in marathon
                    '''
                    port_maps = [
                        MarathonContainerPortMapping(container_port=CONTAINER_PORT, host_port=0,
                                                     service_port=service_port)
                    ]
                    parameters = [{"key": "add-host", "value": "datanode02.yinker.com:10.2.19.83"}, ]
                    docker = MarathonDockerContainer(image='ruoyuchen/jmxexporters', network='BRIDGE',
                                                     port_mappings=port_maps, force_pull_image=True,
                                                     parameters=parameters)
                    container = MarathonContainer(docker=docker)
                    cmd = 'sh /entrypoint.sh ' + inst.host_and_port + ' ' + str(CONTAINER_PORT) + ' ' + \
                          inst.service_type + ' ' + inst.instance_name
                    labels = {'HAPROXY_GROUP': 'will'}
                    health_checks = [
                        MarathonHealthCheck(grace_period_seconds=300, protocol='HTTP', port_index=0, path='/',
                                            timeout_seconds=300,
                                            ignore_http1xx=True, interval_seconds=300, max_consecutive_failures=3), ]
                    new_app = MarathonApp(cmd=cmd, mem=256, cpus=0.5, instances=0, container=container, labels=labels,
                                          health_checks=health_checks)

                    new_result = c.create_app(tmp_id, new_app)
                    time.sleep(3)
                    c.scale_app(tmp_id, delta=1)
                    print('new marathon app %s has been created' % new_result.id)

                    '''
                    add new target and alert rule file to prometheus
                    '''
                    new_app = c.get_app(tmp_id)
                    while new_app.tasks_running != 1:
                        time.sleep(1)
                        new_app = c.get_app(tmp_id)
                        print('No task for {name} yet'.format(name=tmp_id))
                        print(new_app.to_json())
                    task = new_app.tasks[0]
                    port = new_app.ports[0]
                    host = '10.2.19.124'
                    host_port = host + ':' + str(port)
                    with open('{phome}/{service_type}/{app}_online.json'.format(phome=settings.PROMETHEUS_HOME,
                                                                                service_type=inst.service_type,
                                                                                app=inst.instance_name), 'w') as target:
                        target.write('[ {"targets": [ "%s"] }]' % host_port)
                    with open('{phome}/rules/simple_jmx.rule_template'.format(phome=settings.PROMETHEUS_HOME)) as f:
                        temp = f.read()
                        with open('{phome}/rules/{app}.rules'.format(phome=settings.PROMETHEUS_HOME,
                                                                     app=get_clean_jmx_app_id(tmp_id)), 'w') as target:
                            target.write(temp.replace("${alert_name}", inst.instance_name)
                                         .replace("${inst_name}", inst.instance_name)
                                         .replace("${srv_type}", inst.service_type)
                                         .replace("${host_and_port}", inst.host_and_port)
                                         )
                    print('target and rule for %s has been registered to %s' % (tmp_id, settings.PROMETHEUS_HOST))
                    inst.exporter_uri = host_port
                    need_restart = True
                else:
                    print('{tmp_id} is in running ids'.format(tmp_id=tmp_id))
                    c.scale_app(tmp_id, delta=-1)
                    time.sleep(10)
                    c.scale_app(tmp_id, delta=1)
                    print('{tmp_id} has been restarted'.format(tmp_id=tmp_id))
                inst.save()
            except Exception, e:
                print('delete error happended for %s, message is %s' % (inst.instance_name, e.message))
                print traceback.format_exc()

        if need_restart:
            restart_prometheus()
    except Exception, e:
        print('ERROR: %s' % traceback.format_exc())


def get_jmx_app_id(inst):
    hp_inst = inst.host_and_port.replace('.', '').replace(':', '')
    tmp_id = '/' + inst.service_type + '' + hp_inst
    return tmp_id


def get_clean_jmx_app_id(app_id):
    return app_id.replace('/', '')


def get_clean_name(inst):
    return inst.instance_name.replace('-', '_')


@shared_task
def check_new_spark(name='check_new_spark'):
    last_run = redisutils.get_val(REDIS_KEY_SPARK_CHECK_LAST_ADD_TIME)
    print('last run is {ll}'.format(ll=last_run))
    insts = SparkMonitorInstance.objects.filter(utime__gt=last_run, valid=1)
    reset_last_run_time(REDIS_KEY_SPARK_CHECK_LAST_ADD_TIME)
    need_restart = False

    with open('{phome}/rules/simple_spark.rule_template'.format(phome=settings.PROMETHEUS_HOME)) as f:
        temp = f.read()
        for inst in insts:
            try:
                file_name = '{phome}/rules/{app_name}.rules'.format(phome=settings.PROMETHEUS_HOME,
                                                                    app_name=inst.instance_name)
                if not os.path.exists(file_name):
                    '''
                    add new alert rule file to prometheus
                    '''
                    with open('{phome}/rules/%s.rules'.format(phome=settings.PROMETHEUS_HOME), 'w') as target:
                        target.write(temp.replace("${alert_name}", inst.instance_name))
                    need_restart = True
                    print(
                        'spark streaming %s has been registered to %s' % (inst.instance_name, settings.PROMETHEUS_HOST))
            except Exception, e:
                print('delete error happended for %s, message is %s' % (inst.instance_name, e.message))
                print traceback.format_exc()
    if need_restart:
        restart_prometheus()


def reset_last_run_time(k):
    redisutils.set_val(k, django.utils.timezone.now())


@shared_task
def check_disabled_spark(name='check_disabled_spark'):
    last_run = redisutils.get_val(REDIS_KEY_SPARK_CHECK_LAST_MINUS_TIME)
    insts = SparkMonitorInstance.objects.filter(utime__gt=last_run, valid=0)
    reset_last_run_time(REDIS_KEY_SPARK_CHECK_LAST_MINUS_TIME)
    need_restart = False
    for inst in insts:
        try:
            '''
            delete alert rule file to prometheus
            '''
            os.remove('{phome}/rules/{app}.rules'.format(phome=settings.PROMETHEUS_HOME, app=inst.instance_name))
            need_restart = True
            print('spark streaming %s has been unregistered to %s' % (inst.instance_name, settings.PROMETHEUS_HOST))
        except Exception, e:
            print('delete error happended for %s, message is %s' % (inst.instance_name, e.message))
            print traceback.format_exc()
    if need_restart:
        restart_prometheus()


@shared_task
def check_disabled_jmx(name='check_disabled_jmx'):
    last_run = redisutils.get_val(REDIS_KEY_JMX_CHECK_LAST_MINUS_TIME)
    insts = MonitorInstance.objects.filter(utime__gt=last_run, valid=0)
    reset_last_run_time(REDIS_KEY_JMX_CHECK_LAST_MINUS_TIME)
    to_del = set()
    for inst in insts:
        try:
            '''
            delete target file to prometheus
            '''
            os.remove('{phome}/{service_type}/{instance_name}_online.json'.format(phome=settings.PROMETHEUS_HOME,
                                                                                  service_type=inst.service_type,
                                                                                  instance_name=inst.instance_name))
            print('jmx %s has been unregistered to %s' % (inst.instance_name, settings.PROMETHEUS_HOST))

            to_del.add(get_clean_jmx_app_id(get_jmx_app_id(inst)))
            print('jmx {inst_name} alert has been unregistered to {host}'.format(inst_name=inst.instance_name,
                                                                                 host=settings.PROMETHEUS_HOST))
            '''
            delete marathon app
            '''
            app_id = get_jmx_app_id(inst)
            try:
                print('del %s response message: %s' % (app_id, c.delete_app(app_id)))
            except MarathonHttpError, e:
                print traceback.format_exc()
        except Exception, e:
            print('delete error happended for %s, message is %s' % (inst.instance_name, e.message))
            print traceback.format_exc()
    if len(to_del) > 0:
        '''
        delete alert rule file to prometheus
        '''
        for ii in to_del:
            os.remove('{phome}/rules/{app}.rules'.format(phome=settings.PROMETHEUS_HOME, app=ii))
        # cmd = (' && ').join(['rm -vf {phome}/rules/%s.rules' % ii for ii in to_del])
        # local_cmd(cmd)
        ss = requests.post('http://{phost}:9090/-/reload'.format(phost=settings.PROMETHEUS_HOST))
        ss.raise_for_status()
        print('prometheus has been restarted')


def restart_prometheus():
    ss = requests.post('http://{phost}:9090/-/reload'.format(phost=settings.PROMETHEUS_HOST))
    ss.raise_for_status()
    print('prometheus has been restarted')

# def local_cmd(command):
#     p = subprocess.Popen([''.join(command)], stderr=subprocess.STDOUT,
#                          shell=True,
#                          universal_newlines=True)
#     p.wait()
#     returncode = p.returncode
#     logger.info('%s return code is %d' % (command, returncode))

# def remote_cmd(remote_cmd, target_host=settings.PROMETHEUS_HOST):
#     '''
#     run command on the prometheus remote host useing fabric
#     :param remote_cmd:
#     :return:
#     '''
#     from fabric.api import run
#     from fabric.api import env
#     env.host_string = target_host
#     result = run(remote_cmd)
#     env.host_string = ''
#     return result
