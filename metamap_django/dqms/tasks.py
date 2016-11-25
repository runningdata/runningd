# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will
'''

from __future__ import absolute_import

import logging
import os
import subprocess
import traceback

from celery import shared_task, task
from django.utils import timezone

from dqms.models import DqmsCheckInst, DqmsCheck, DqmsCase, DqmsCaseInst, DqmsAlert

from celery.utils.log import get_task_logger

from metamap_django import settings
from will_common.models import UserProfile
from will_common.utils import PushUtils
from will_common.utils import dateutils
from will_common.utils import encryptutils
from will_common.utils import enums
from will_common.utils import hivecli
from will_common.utils import constants
from will_common.utils import mysqlcli

logger = get_task_logger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(__file__)) + '/dqms/'

@shared_task
def exec_dqms(task_id):
    check = DqmsCheck.objects.get(pk=task_id)
    check.last_run_time = timezone.now()
    check.save()
    chk_inst = DqmsCheckInst.objects.create(chk=check, case_num=check.cases.count())
    chk_inst.save()
    try:
        for case in check.cases.all():
            runcase(case, check, None)
            chk_inst.case_finish_num += 1
            chk_inst.save()
        chk_inst.end_time = timezone.now()
        chk_inst.save()
    except Exception, e:
        logger.error('ERROR: %s' % traceback.format_exc())
        chk_inst.end_time = timezone.now()
        chk_inst.save()


@shared_task()
def run_case(case_id, user_id):
    case = DqmsCase.objects.get(pk=case_id)
    user = UserProfile.objects.get(user_id=user_id)
    runcase(case, None, user)


def runcase(case, check, user):
    chk_name = 'test'
    if check:
        chk_name = check.chk_name
    logger.info('processing %s ' % case.case_name)
    case_inst = DqmsCaseInst(case=case, status=enums.EXECUTION_STATUS.RUNNING)
    case_inst.save()
    try:
        if case.datasrc.src_type == constants.DATASRC_TYPE_HIVE:
            result = hivecli.execute(case.sql_pattern)
        elif case.datasrc.src_type == constants.DATASRC_TYPE_MYSQL:
            result = mysqlcli.execute(constants.DATASRC_TYPE_MYSQL_DB, case.sql_pattern)
        else:
            logger.error('cannot recognize datasource type :', case.datasrc.src_type)
        if result:
            for rule in case.dqmsrule_set.all():
                print('handleing %s ' % rule.measure_column)
                re = result[rule.measure_column]
                print('result is %d , max is %d, min is %d' % (re, rule.max, rule.min))
                if re > rule.max or re < rule.min:
                    alert = DqmsAlert.objects.create(rule=rule)
                    msg = constants.ALERT_MSG % (
                        dateutils.format_dbday(timezone.now()), chk_name, case.case_name, rule.measure_name, rule.min, rule.max, re)
                    if check:
                        PushUtils.push_msg_tophone(case.editor.phone, msg)
                        resp = PushUtils.push_msg(check.managers.all(), msg)
                        phones = ''
                        for user in check.managers.all():
                            phones = phones + ',' + str(user.phone)
                        alert.target_phone = phones
                        alert.owners = check.managers.all()
                    elif user:
                        resp = PushUtils.push_msg([user, ], msg)
                        alert.target_phone = user.phone
                        alert.owners = [user, ]
                    alert.push_msg = msg
                    alert.push_resp = resp
                    alert.save()
                    print('alerting for case %s -> rule : %s ' % (case.case_name, rule.measure_name))
        case_inst.status = enums.EXECUTION_STATUS.DONE
        case_inst.result_mes = 'success'
    except Exception, e:
        logger.error(e.message)
        print('msg : %s ' % traceback.format_exc())
        PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE), traceback.format_exc())
        case_inst.status = enums.EXECUTION_STATUS.FAILED
        case_inst.result_mes = e.message
    case_inst.save()
