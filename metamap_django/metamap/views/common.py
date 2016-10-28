# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django.http import HttpResponse
from django.shortcuts import render


def h500(request):
    return render(request, 'common/500.html')

def h404(request):
    return render(request, 'common/404.html')

def not_login(request):
    return HttpResponse('nothing')