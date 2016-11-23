# -*- coding: utf-8 -*
import logging
import urllib2

from metamap_django import settings
from will_common.utils.encryptutils import encrpt_msg


def push_msg(users, msg):
    for user in users:
        push_msg_tophone(user.phone, msg)
    return 'push success'


def push_msg_tophone(phone, msg):
    logging.info('alert happening: %s : %s' % (phone, msg))

    req = urllib2.Request(
        settings.PUSH_URL % (encrpt_msg(phone), encrpt_msg(msg)))
    try:
        resp = urllib2.urlopen(req)
        if resp.getcode() == 200:
            print resp.read()
            return 'push phone success'
        else:
            return 'error', resp.read()
    except urllib2.URLError, e:
        return e.reason


# s = push_msg_tophone('1232213232', 'sd')
# print s
