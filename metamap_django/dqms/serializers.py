# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from rest_framework import serializers

from dqms.models import DqmsDatasource, DqmsCase, DqmsRule


class DqmsDatasourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsDatasource
        fields = ('src_name', 'valid', 'id')

class DqmsCaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsCase
        fields = ('case_name', 'creator', 'id', 'utime', 'ctime', 'remark')

class DqmsRuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsRule
        fields = ('rule_type', 'remark',  'ctime',  'utime', 'min', 'max', 'measure_desc', 'measure_name', 'measure_type', 'rule_predicate')

