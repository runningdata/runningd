# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.contrib.auth.models import Group
from rest_framework import serializers


class WillDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', api_settings.DATETIME_FORMAT)

        if output_format is None or isinstance(value, six.string_types):
            return value

        if output_format.lower() == ISO_8601:
            value = value.isoformat()
            if value.endswith('+00:00'):
                value = value[:-6] + 'Z'
            return value
        tz = pytz.timezone('Asia/Shanghai')
        return value.astimezone(tz).strftime(output_format)


class GroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'id')
