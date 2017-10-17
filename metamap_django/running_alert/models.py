# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

# Create your models here.
from will_common.models import CommmonTimes, CommmonCreators
from django.db.models.signals import post_save
from django.dispatch import receiver


class MonitorInstance(CommmonTimes, CommmonCreators):
    '''
    Server like flume, kafka, zookeeper, which has jmx port avaliable

    For spark_streaming_app which use dynamic app discovery, host_and_port is not necessary, we can ignore it.
    '''
    host_and_port = models.CharField(max_length=50, blank=False, null=False, verbose_name=u'目标主机:端口号[10.2.16.81:4545]', unique=True)
    instance_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=u'监控名称', unique=True)
    exporter_uri = models.CharField(max_length=50, blank=False, null=False, verbose_name=u'监控指标地址')
    managers = models.CharField(max_length=300, blank=False, null=False, default='', verbose_name=u'告警接收人[逗号隔开]')
    service_type = models.CharField(max_length=50, blank=False, null=False, verbose_name=u'实例类型', choices=(
        ('kafka', 'kafka'), ('zookeeper', 'zookeeper'), ('flume', 'flume'), ('tomcat', 'tomcat'), ('azkaban', 'azkaban'),
        # ('spark_streaming_app', 'spark_streaming_app')
    ))
    valid = models.IntegerField(default=1, verbose_name=u'是否有效', choices=(
        (1, '是'),
        (0, '否'),
    ))


class SparkMonitorInstance(CommmonTimes, CommmonCreators):
    '''
    Server like flume, kafka, zookeeper, which has jmx port avaliable

    For spark_streaming_app which use dynamic app discovery, host_and_port is not necessary, we can ignore it.
    '''
    instance_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=u'监控名称')
    managers = models.CharField(max_length=300, blank=False, null=False, default='', verbose_name=u'告警接收人[逗号隔开]')
    exporter_uri = models.CharField(max_length=50, blank=False, null=False, verbose_name=u'监控指标地址', default=settings.SPARK_EXPORTER_HOST)
    valid = models.IntegerField(default=1, verbose_name=u'是否有效', choices=(
        (1, '是'),
        (0, '否'),
    ))


@receiver(post_save, sender=MonitorInstance)
def update_marathon(sender, instance, **kwargs):
    print('%s saved' % instance.instance_name)


class ServiceRules(CommmonTimes):
    '''
    Alert rules for each service
    '''
    service_name = models.CharField(max_length=50, blank=False, null=False, verbose_name=u'服务类型', choices=(
        ('kafka', 'kafka'), ('zookeeper', 'zookeeper'), ('flume', 'flume'), ('tomcat', 'tomcat'), ('azkaban', 'azkaban'),
        # ('spark_streaming_app', 'spark_streaming_app')
    ))
    rules = models.TextField(verbose_name=u'告警规则')
