# -*- coding: utf-8 -*
import logging
import urllib2

from metamap_django import settings
from will_common.utils.encryptutils import encrpt_msg

push_url = settings.PUSH_URL


def push_msg(users, msg):
    for user in users:
        push_msg_tophone(user.phone, msg)
    return 'push success'


def push_msg_tophone(phone, msg):
    logging.info('alert happening: %s : %s' % (phone, msg))

    req = urllib2.Request(
        push_url % (encrpt_msg(phone), encrpt_msg(msg)))
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
    try:
        resp = urllib2.urlopen(req)
        if resp.getcode() == 200:
            print resp.read()
            return 'push phone success'
        else:
            return 'error', resp.read()
    except urllib2.URLError, e:
        return e.reason
