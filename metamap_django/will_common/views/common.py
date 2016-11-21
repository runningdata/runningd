# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from django.shortcuts import render, redirect


def h500(request):
    return render(request, 'common/500.html')

def h404(request):
    return render(request, 'common/404.html')

def redir_dqms(request):
    return redirect('/dqms')

def redir_metamap(request):
    return redirect('/metamap')