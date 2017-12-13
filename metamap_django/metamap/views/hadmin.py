# -*- coding: utf-8 -*
import logging
import traceback

from django.conf import settings
import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from will_common.djcelery_models import AuthPermission, AuthUserUserPermissions, AuthUser, AuthUserGroups, AuthGroup
from will_common.models import UserProfile
from will_common.utils import PushUtils
from will_common.utils.customexceptions import RDException

logger = logging.getLogger('django')


def add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                group = request.user.userprofile.org_group
                # check all
                email = request.POST['email'].strip()
                username = email.replace(settings.result['ORG_EMAIL_SUFFIX'], '').strip()
                if 'export' in request.POST or 'xstorm' in request.POST:
                    if not User.objects.filter(username=username, email=email).exists():
                        user = User.objects.create(username=username, email=email, last_login=timezone.now(),
                                                   date_joined=timezone.now(),
                                                   is_active=1, is_staff=0)
                        user.set_password(settings.DEFAULT_PASSWD)
                        user.save()
                    else:
                        user = User.objects.get(username=username, email=email)
                        user.is_active = 1
                        user.save()
                    UserProfile.objects.get_or_create(user=user, phone=request.POST['phone'], org_group=group)
                    permission = AuthPermission.objects.get(codename='access_etl')
                    auth_user = AuthUser.objects.get(username=user.username)
                    if 'xstorm' in request.POST:
                        AuthUserUserPermissions.objects.get_or_create(permission=permission, user=auth_user)
                    else:
                        if AuthUserUserPermissions.objects.filter(permission=permission, user=auth_user).exists():
                            AuthUserUserPermissions.objects.get(permission=permission, user=auth_user).delete()
                else:
                    if User.objects.filter(username=username, email=email).exists():
                        user = User.objects.get(username=username, email=email)
                        user.is_active = 0
                        user.save()
                if 'hue' in request.POST:
                    if User.objects.using(settings.DB_HUE).filter(username=username, email=email).exists():
                        user = User.objects.using(settings.DB_HUE).get(username=username, email=email)
                        user.is_active = 1
                        user.save()
                        print ('user %s for hue already exist' % username)
                    else:
                        user = User.objects.using(settings.DB_HUE).create(username=username, email=email,
                                                                          last_login=timezone.now(),
                                                                          date_joined=timezone.now(),
                                                                          is_active=1, is_staff=0)
                        user.set_password(settings.DEFAULT_PASSWD)
                        user.save()
                        auth_user = AuthUser.objects.using(settings.DB_HUE).get(username=user.username)
                        auth_group = AuthGroup.objects.using(settings.DB_HUE).get(name__iexact=group.name)
                        AuthUserGroups.objects.using(settings.DB_HUE).get_or_create(user=auth_user, group=auth_group)
                        from fabric.api import run
                        from fabric.api import env
                        for hhost in settings.NN_HOSTS:
                            env.host_string = hhost
                            print run('useradd %s -G %s' % (username, group.name))
                        env.host_string = ''
                else:
                    if User.objects.using(settings.DB_HUE).filter(username=username, email=email).exists():
                        user = User.objects.get(username=username, email=email)
                        user.is_active = 0
                        user.save()
                PushUtils.push_both(UserProfile.objects.filter(user_id=1), '%s auth changed by %s, to %s ' % (
                    username, request.user.username, json.dumps(request.POST)))
                return HttpResponseRedirect(reverse('hadmin:hadmin_add'))
        except RDException, e:
            return render(request, 'common/message.html', {'message': e.message, 'err_stack': e.err_stack})
        except Exception, e:
            print(traceback.format_exc())
            return render(request, 'common/message.html', {'message': e.message, 'err_stack': traceback.format_exc()})
    else:
        xstorm_users = UserProfile.objects.filter(org_group=request.user.userprofile.org_group).order_by(
            '-user__is_active')
        hue_users = AuthUserGroups.objects.using(settings.DB_HUE).filter(
            group__name=request.user.userprofile.org_group.name).order_by(
            '-user__is_active')
        return render(request, 'hadmin/edit.html', {'xstorm_users': xstorm_users, 'hue_users': hue_users})
