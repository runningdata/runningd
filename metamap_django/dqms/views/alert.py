from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from dqms.models import DqmsRule, DqmsAlert
from dqms.serializers import DqmsRuleSerializer

def manager(request):
    alerts = DqmsAlert.objects.all()
    return render(request, 'alert/info.html', {'objs' : alerts})

