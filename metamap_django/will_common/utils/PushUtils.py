# -*- coding: utf-8 -*
import logging
import traceback
import urllib2

from django.conf import settings
from django.core.mail import BadHeaderError
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
            push_msg_tophone(user_p.phone, msg)
        return 'push success'
    except Exception, e:
        return 'push error : %s' % str(e)


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


def push_exact_html_email(email, subject, msg):
    try:
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, msg, from_email, [email, ])
        msg.content_subtype = 'html'
        msg.send()
        return 'success'
    except Exception as e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return 'error : %s ' % e


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