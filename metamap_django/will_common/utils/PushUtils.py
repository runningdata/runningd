# -*- coding: utf-8 -*
import logging
import urllib2

import requests
from django.conf import settings

from will_common.utils.encryptutils import encrpt_msg

push_url = settings.PUSH_URL


def push_msg(users, msg):
    try:
        for user in users:
            push_msg_tophone(user.phone, msg)
        return 'push success'
    except Exception, e:
        return 'push error : %s' % str(e)


def push_msg_tophone(phone, msg):
    msg_ = push_url % (encrpt_msg(phone), encrpt_msg(msg))
    req = urllib2.Request(msg_)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
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
