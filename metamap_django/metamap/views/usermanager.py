# -*- coding: utf-8 -*
import logging
import traceback

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from will_common.models import UserProfile

logger = logging.getLogger('django')

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         # fields = ['user', 'org_group', 'phone']
#         exclude = ()
#
# # def add_user(request):
# class UserForm(UserChangeForm):
#     class Meta:
#         model = User
#         exclude = ()
#
#     def __init__(self, *args, **kwargs):
#         super(UserForm, self).__init__(*args, **kwargs)
#         student_kwargs = kwargs.copy()
#         if kwargs.has_key('instance'):
#             self.student = kwargs['instance'].userprofile
#             student_kwargs['instance'] = self.userprofile
#         self.userprofile_form = UserProfileForm(*args, **student_kwargs)
#         self.fields.update(self.userprofile_form.fields)
#         self.initial.update(self.userprofile_form.initial)
#
#         # # define fields order if needed
#         # self.fields.keyOrder = (
#         #     'last_name',
#         #     'first_name',
#         #     'phone'
#         # )
#
#     def clean(self):
#         cleaned_data = super(UserForm, self).clean()
#         self.errors.update(self.userprofile_form.errors)
#         return cleaned_data
#
#     def save(self, commit=True):
#         self.userprofile_form.save(commit)
#         return super(UserForm, self).save(commit)
#
# class UserCreaForm(UserCreationForm):
#     class Meta:
#         model = User
#         exclude = ()
#
#     def __init__(self, *args, **kwargs):
#         super(UserCreaForm, self).__init__(*args, **kwargs)
#         student_kwargs = kwargs.copy()
#         if kwargs.has_key('instance'):
#             self.student = kwargs['instance'].userprofile
#             student_kwargs['instance'] = self.userprofile
#         self.userprofile_form = UserProfileForm(*args, **student_kwargs)
#         self.fields.update(self.userprofile_form.fields)
#         self.initial.update(self.userprofile_form.initial)
#
#     def clean(self):
#         cleaned_data = super(UserCreaForm, self).clean()
#         self.errors.update(self.userprofile_form.errors)
#         return cleaned_data
#
#     def save(self, commit=True):
#         self.userprofile_form.save(commit)
#         return super(UserCreaForm, self).save(commit)

# def add_user(request):
    # if request.method == 'POST':
    #     try:
    #         current_org = request.user.userprofile.org_group
    #         form = UserCreationForm(request.POST)
    #         if form.is_valid():
    #             xx = form.save()
    #             UserProfile.objects.get_or_create(user=xx, org_group=current_org, phone=phone)
    #         else:
    #             form = UserCreationForm(request.POST)
    #             return render(request, 'usermanger/post_edit.html', {'form': form})
    #         return HttpResponseRedirect(reverse('metamap:jar_index'))
    #     except Exception, e:
    #         return render(request, 'common/500.html', {'msg': traceback.format_exc().replace('\n', '<br>')})
    # else:
    #     form = UserCreaForm()
    #     return render(request, 'usermanger/post_edit.html', {'form': form})

def list_user(request):
    users = UserProfile.objects.filter(org_group=request.user.userprofile.org_group)
    return render(request, 'usermanger/list.html', {'objs': users})