# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import os
import random
import traceback

import time
from celery import shared_task
#
from celery.utils.log import get_task_logger
from django.conf import settings
from marathon import MarathonApp
from marathon import MarathonClient
from marathon.models.container import MarathonContainer, MarathonDockerContainer, MarathonContainerPortMapping

from running_alert.models import MonitorInstance

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/running_alert/'

c = MarathonClient('http://10.1.5.190:8080')

metric_files = dict()
metric_files['flume'] = '/flume_sample.yaml'
metric_files['kafka'] = '/kafka_sample.yaml'
metric_files['zookeeper'] = '/zookeeper_sample.yaml'
CONTAINER_PORT = 1234
prometheus_container = 'my-prometheus'


def get_avaliable_port():
    from fabric.api import run
    from fabric.api import env
    env.host_string = settings.PROMETHEUS_HOST
    rxe = run('netstat -lntu | awk \'{print($4)}\' | grep : | awk -F \':\' \'{print $NF}\' | sort -nru ')
    used_ports = [int(i) for i in rxe.split('\r\n')]
    min_port = used_ports[-1]
    start_port = min_port if min_port > settings.START_PORT else settings.START_PORT
    start_port = start_port + random.randint(1, 30000)
    while start_port in used_ports:
        start_port = start_port + 1
    return start_port


@shared_task
def check_new_inst(name='check_new_inst'):
    try:
        last_run = 'get from db or local file'
        insts = MonitorInstance.objects.filter(utime__gt=last_run)
        for inst in insts:
            running_ids = [app.id for app in c.list_apps()]
            hp_inst = inst.host_and_port.replace('.', '_').replace(':', '_')
            tmp_id = '/' + inst.service_type + '__' + hp_inst
            host_port = get_avaliable_port()
            service_port = 0
            if tmp_id not in running_ids:
                '''
                run the docker container in marathon
                '''
                port_maps = [
                    MarathonContainerPortMapping(container_port=CONTAINER_PORT, host_port=host_port,
                                                 service_port=service_port)
                ]
                parameters = [{"key": "add-host", "value": "datanode02.yinker.com:10.2.19.83"}, ]
                docker = MarathonDockerContainer(image='ruoyuchen/jmxexporters', network='BRIDGE',
                                                 port_mappings=port_maps, force_pull_image=True, parameters=parameters)
                container = MarathonContainer(docker=docker)
                cmd = 'sh /entrypoint.sh ' + inst.host_and_port + CONTAINER_PORT + ' ' + metric_files[
                    inst.service_type] + tmp_id
                # domain_name = hp_inst + '.' + inst.service_type + '.moniter.com'
                # labels = {'HAPROXY_GROUP': 'external',
                #           'HAPROXY_0_VHOST': domain_name}
                # new_app = MarathonApp(cmd=cmd, mem=32, cpus=0.25, instances=1, container=container, labels=labels)
                #
                # new_result = c.create_app(tmp_id, new_app)
                # logger.info('new app %s has been created' % new_result.id)
                #
                # '''
                # add new target and alert rule file to prometheus
                # '''
                # echo_command = 'echo "10.1.5.190 %s">> /tmp/prometheus/hosts  ' % domain_name
                # target_command = ' && echo \'[ {"targets": [ "%s"] }]\' > /tmp/prometheus/sds/%s_online.json ' % (domain_name, domain_name)
                # rule_command = ' && sed -e \'s/${alert_name}/%s/g\' -e \'s/${target}/%s/g\' -e \'s/${srv_type}/%s/g\' /tmp/prometheus/rules/simple_jmx.rule_template > /tmp/prometheus/rules/%s.rules ' % (
                #     tmp_id, domain_name, inst.service_type, domain_name)
                # restart_command = ' && docker restart %s' % prometheus_container
                labels = {}
                new_app = MarathonApp(cmd=cmd, mem=32, cpus=0.25, instances=1, container=container, labels=labels)

                new_result = c.create_app(tmp_id, new_app)
                logger.info('new app %s has been created' % new_result.id)

                '''
                add new target and alert rule file to prometheus
                '''
                echo_command = ' echo ccc'
                target_command = ' && echo \'[ {"targets": [ "%s"] }]\' > /tmp/prometheus/sds/%s_online.json ' % (
                    inst.host_and_port, tmp_id)
                rule_command = ' && sed -e \'s/${alert_name}/%s/g\' -e \'s/${target}/%s/g\' -e \'s/${srv_type}/%s/g\' /tmp/prometheus/rules/simple_jmx.rule_template > /tmp/prometheus/rules/%s.rules ' % (
                    tmp_id, inst.host_and_port, inst.service_type, tmp_id)
                restart_command = ' && docker restart %s' % prometheus_container
                from fabric.api import run
                from fabric.api import env

                env.host_string = settings.PROMETHEUS_HOST
                print run(
                    echo_command
                    + target_command +
                    + rule_command + restart_command
                )
                logger.info('domain %s has been registered to %' % (tmp_id, settings.PROMETHEUS_HOST))
                env.host_string = ''
            else:
                c.scale_app(id, delta=-1)
                time.sleep(10)
                c.scale_app(id, delta=1)
            inst.exporter_uri = host_port
            inst.save()
    except Exception, e:
        logger.error('ERROR: %s' % traceback.format_exc())
