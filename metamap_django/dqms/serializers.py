# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from rest_framework import serializers

from dqms.models import DqmsDatasource, DqmsCase, DqmsRule, DqmsCheckInst, DqmsCaseInst


class DqmsDatasourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsDatasource
        fields = ('src_type', 'src_name', 'valid', 'id')

class DqmsCaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsCase
        fields = ('case_name', 'id', 'utime', 'ctime', 'remark')

class DqmsCheckInstSerializer(serializers.HyperlinkedModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = DqmsCheckInst
        fields = ('case_num', 'case_finish_num', 'start_time', 'end_time', 'result_code', 'result_mes')

class DqmsCaseInstSerializer(serializers.HyperlinkedModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = DqmsCaseInst
        fields = ('start_time', 'end_time', 'status', 'result_mes')

class DqmsRuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DqmsRule
        fields = ('refer','rule_type', 'remark',  'ctime',  'utime', 'min', 'max', 'measure_desc', 'measure_name', 'measure_type', 'rule_predicate', 'measure_column')

