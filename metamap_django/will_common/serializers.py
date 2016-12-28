# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.contrib.auth.models import Group
from rest_framework import serializers


class GroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'id')

