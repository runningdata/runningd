from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from metamap import models


class DataSource(models.Model):
    '''
       数据库对应meta
    '''
    name = models.CharField(max_length=30, unique=True)
    settings = models.CharField(max_length=300, null=True)
    type = valid = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)


class Rule(models.Model):
    '''
       数据库对应meta
    '''
    name = models.CharField(max_length=30, unique=True)
    settings = models.CharField(max_length=300, null=True)
    type = valid = models.IntegerField(default=1)
    ctime = models.DateTimeField(default=timezone.now)
    valid = models.IntegerField(default=1)
