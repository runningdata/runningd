# -*- coding: utf-8 -*
import json
import logging
import traceback
import urllib2
from smtplib import SMTPDataError, SMTPAuthenticationError

import requests
from django.conf import settings
from django.core.mail import BadHeaderError, get_connection
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.http import HttpResponse

from will_common.models import UserProfile
from will_common.utils import regxutils
from will_common.utils.encryptutils import encrpt_msg

push_url = settings.PUSH_URL
logger = logging.getLogger('django')


def push_msg(user_profiles, msg):
    try:
        for user_p in user_profiles:
            if user_p.user.is_active == 1:
                push_msg_tophone(user_p.phone, msg)
            else:
                logger.info('no valid user for %s ' % user_p.user.username)
        return 'push success'
    except Exception, e:
        return 'push error : %s' % str(e)


def push_to_admin(msg):
    user_profiles = [UserProfile.objects.get(user__username='admin')]
    push_msg(user_profiles, msg)
    push_email([user_p.user for user_p in user_profiles], msg)
    return 'push both to admin success'


def push_wechat(user_profiles, msg):
    try:
        users = [user.user.username for user in user_profiles]
        payload = {'agentid': '1000009', 'touser': '|'.join(users), 'text': msg}
        r = requests.post(settings.WECHAT_ALERT_URL, data=json.dumps(payload),
                          headers={'Content-Type': 'application/json'}, timeout=60)
        if r.status_code != 200:
            raise Exception(u'failed to send wechat {msg}'.format(msg=msg))
            return 'success'
        else:
            return 'error', r.text
    except Exception as e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())


def push_to_admin(msg):
    user_profiles = [UserProfile.objects.get(user__username='admin')]
    push_msg(user_profiles, msg)
    push_email([user_p.user for user_p in user_profiles], msg)
    return 'push both to admin success'


def push_msg_tophone(phone, msg):
    try:
        msg_ = push_url % (encrpt_msg(phone), encrpt_msg(msg))
        req = urllib2.Request(msg_)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
        httpHandler = urllib2.HTTPHandler(debuglevel=0)
        httpsHandler = urllib2.HTTPSHandler(debuglevel=0)
        opener = urllib2.build_opener(httpHandler, httpsHandler)
        urllib2.install_opener(opener)
        resp = urllib2.urlopen(req)
        content = resp.read()
        if resp.getcode() == 200 and content != '"ERROR"':
            logger.info(content)
            return 'success'
        else:
            return 'error', content
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return 'error : %s ' % e


def push_both(user_profiles, msg):
    push_msg(user_profiles, msg)
    push_wechat(user_profiles, msg)
    push_email([user_p.user for user_p in user_profiles], msg)
    return 'push both success'


def push_email(users, msg):
    try:
        subject = 'Alert From XStorm'
        from_email = settings.EMAIL_HOST_USER
        emails = [user.email for user in users if user.email and regxutils.check_email(user.email)]
        if subject and msg and from_email:
            try:
                send_mail(subject, msg, from_email, emails)
                print('pushed done to %s ' % emails)
            except BadHeaderError:
                logger.error('Invalid header found for %s .' % emails)
        else:
            logger.error('Make sure all fields are entered and valid.')
    except Exception as e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())


def push_data_wechat(msg):
    '''
    Just send wechat alert to data team
    :param msg:
    :return:
    '''
    try:
        payload = {'agentid': '1000009', 'totag': '9', 'text': msg}
        r = requests.post(settings.WECHAT_ALERT_URL, data=json.dumps(payload),
                          headers={'Content-Type': 'application/json'}, timeout=60)
        if r.status_code != 200:
            raise Exception(u'failed to send wechat {msg}'.format(msg=msg))
            return 'success'
        else:
            return 'error', r.text
    except Exception as e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())


def push_exact_html_email(email, subject, msg):
    error_msg = ''
    for k, v in settings.EMAIL_CANDIDATES.items():
        try:
            from_email = k
            em = EmailMessage(subject=subject, body=msg, from_email=from_email, to=[email, ],
                              connection=get_connection(username=k, password=v))
            em.content_subtype = 'html'
            em.send()
            logger.info('email sent successful from %s' % k)
            return 'success'
        except SMTPAuthenticationError, e:
            error_msg = 'error : %s using %s' % (e, k)
            logger.error(error_msg)
            logger.error('traceback is : %s ' % traceback.format_exc())
        except SMTPDataError, e:
            error_msg = 'error : %s using %s' % (e, k)
            logger.error(error_msg)
            logger.error('traceback is : %s ' % traceback.format_exc())
        except Exception as e:
            error_msg = 'error : %s using %s' % (e, k)
            logger.error(error_msg)
            logger.error('traceback is : %s ' % traceback.format_exc())
    return error_msg


def push_exact_email(email, msg):
    try:
        subject = 'Alert From XStorm'
        from_email = settings.EMAIL_HOST_USER
        if subject and msg and from_email:
            try:
                send_mail(subject, msg, from_email, [email, ])
            except BadHeaderError:
                logger.error('Invalid header found for %s .' % email)
        else:
            logger.error('Make sure all fields are entered and valid.')
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
