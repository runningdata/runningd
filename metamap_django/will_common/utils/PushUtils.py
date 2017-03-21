# -*- coding: utf-8 -*
import logging
import urllib2

from django.conf import settings
from django.core.mail import BadHeaderError
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.http import HttpResponse

from will_common.utils.encryptutils import encrpt_msg

push_url = settings.PUSH_URL


def push_msg(user_profiles, msg):
    try:
        for user_p in user_profiles:
            push_msg_tophone(user_p.phone, msg)
        return 'push success'
    except Exception, e:
        return 'push error : %s' % str(e)


def push_msg_tophone(phone, msg):
    msg_ = push_url % (encrpt_msg(phone), encrpt_msg(msg))
    req = urllib2.Request(msg_)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
    httpHandler = urllib2.HTTPHandler(debuglevel=1)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
    opener = urllib2.build_opener(httpHandler, httpsHandler)
    urllib2.install_opener(opener)
    resp = urllib2.urlopen(req)
    if resp.getcode() == 200:
        print resp.read()
        return 'push phone success'
    else:
        return 'error', resp.read()


def push_both(user_profiles, msg):
    push_email([user_p.user for user_p in user_profiles], msg)
    push_msg(user_profiles, msg)


def push_email(users, msg):
    subject = 'Alert From XStorm'
    from_email = settings.EMAIL_HOST_USER
    emails = [user.email for user in users]
    if subject and msg and from_email:
        try:
            send_mail(subject, msg, from_email, emails)
        except BadHeaderError:
            return 'Invalid header found.'
        return 'Ok header found.'
    else:
        return 'Make sure all fields are entered and valid.'

def push_exact_email(email, msg):
    subject = 'Alert From XStorm'
    from_email = settings.EMAIL_HOST_USER
    if subject and msg and from_email:
        try:
            send_mail(subject, msg, from_email, [email, ])
        except BadHeaderError:
            return 'Invalid header found.'
        return 'Ok header found.'
    else:
        return 'Make sure all fields are entered and valid.'

def push_email2(request):
    subject = request.POST.get('subject', 'willtest')
    message = request.POST.get('message', 'willtest')
    from_email = request.POST.get('from_email', 'yinkerconfluence@yinker.com')
    if subject and message and from_email:
        try:
            email = EmailMessage(
                u'中文题目',
                u'中文内容',
                'yinkerconfluence@yinker.com',
                ['chenxin@yinker.com'],
                ['xuexu@yinker.com'],
            )
            email.attach_file(u'/root/月度目标数据-20170210095000')

            email.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse('Ok header found.')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')
