# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from django import forms
from django.contrib import auth
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views import generic
from rest_framework import viewsets

from will_common.models import OrgGroup
from will_common.serializers import GroupsSerializer


def navigate(request):
    return render(request, 'common/navigate.html')


class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"原密码",
            }
        ),
    )
    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"新密码",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"确认密码",
            }
        ),
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif self.cleaned_data['newpassword2'] <> self.cleaned_data['newpassword1']:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data


def modify_pwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('common/modify.html', RequestContext(request, {'form': form, }))
    else:
        with transaction.atomic():
            form = ChangepwdForm(request.POST)
            if form.is_valid():
                username = request.user.username
                oldpassword = request.POST.get('oldpassword', '')
                user = auth.authenticate(username=username, password=oldpassword)
                if user is not None and user.is_active:
                    newpassword = request.POST.get('newpassword1', '')
                    user.set_password(newpassword)
                    user.save()
                    return redirect('/')
                else:
                    return render_to_response('common/modify.html',
                                              RequestContext(request, {'form': form, 'oldpassword_is_wrong': True}))
            else:
                return render_to_response('common/modify.html', RequestContext(request, {'form': form, }))


def h500(request):
    return render(request, 'common/500.html')


def h404(request):
    return render(request, 'common/404.html')


def redir_dqms(request):
    return redirect('/dqms')


def redir_metamap(request):
    return redirect('/metamap')


from django.utils.translation import ugettext as _


class GroupListView(generic.ListView):
    def get(self, request, *args, **kwargs):
        if request.user.username != 'admin':
            current_group = self.request.user.userprofile.org_group
            self.object_list = self.get_queryset().filter(cgroup=current_group)
        else:
            self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                              % {'class_name': self.__class__.__name__})
        context = self.get_context_data()
        return self.render_to_response(context)


class GroupsViewSet(viewsets.ModelViewSet):
    queryset = OrgGroup.objects.all()
    serializer_class = GroupsSerializer
