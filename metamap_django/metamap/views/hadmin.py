# -*- coding: utf-8 -*
import logging
import traceback

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.datetime_safe import datetime

from will_common.djcelery_models import AuthPermission, AuthUserUserPermissions, AuthUser, AuthUserGroups, AuthGroup
from will_common.models import WillDependencyTask, UserProfile
from will_common.utils.customexceptions import RDException

logger = logging.getLogger('django')


def add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                group = request.user.userprofile.org_group
                # check all
                email = request.POST['email']
                username = email.replace('@yinker.com', '')
                if 'export' or 'xstorm' in request.POST:
                    if not User.objects.using(settings.DB_HUE).filter(username=username, email=email).exists():
                        user, created = User(username=username, email=email, last_login=timezone.now(), date_joined=timezone.now(),
                                is_active=1, is_staff=0, )
                        user.set_password(settings.DEFAULT_PASSWD)
                        user.save()
                    else:
                        user = User.objects.get(username=username, email=email)
                    UserProfile.objects.get_or_create(user=user, phone=request.POST['phone'], org_group=group)
                    if 'xstorm' in request.POST:
                        permission = AuthPermission.objects.get(codename='access_etl')
                        auth_user = AuthUser.objects.get(username=user.username)
                        AuthUserUserPermissions.objects.get_or_create(permission=permission, user=auth_user)
                if 'hue' in request.POST:
                    if User.objects.using(settings.DB_HUE).filter(username=username, email=email).exists():
                        return HttpResponse('already exist')
                    user = User(username=username, email=email, last_login=timezone.now(), date_joined=timezone.now(),
                                is_active=1, is_staff=0, )
                    user.set_password(settings.DEFAULT_PASSWD)
                    user.save()
                    if 'xstorm' in request.POST:
                        auth_user = AuthUser.objects.using(settings.DB_HUE).get(username=user.username)
                        auth_group = AuthGroup.objects.using(settings.DB_HUE).get(name=group.name)
                        AuthUserGroups.objects.using(settings.DB_HUE).get_or_create(user=auth_user, group=auth_group)
                    from fabric.api import run
                    from fabric.api import env
                    for hhost in settings.NN_HOSTS:
                        env.host_string = hhost
                        print run('useradd %s -G %s' % (username, group.name))
                    env.host_string = ''
                return render(request, 'hadmin/edit.html')
        except RDException, e:
            return render(request, 'common/message.html', {'message': e.message, 'err_stack': e.err_stack})
        except Exception, e:
            print(traceback.format_exc())
            return render(request, 'common/message.html', {'message': e.message, 'err_stack': traceback.format_exc()})
    else:
        return render(request, 'hadmin/edit.html')
