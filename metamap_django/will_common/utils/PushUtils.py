# -*- coding: utf-8 -*
import logging
import urllib2

import requests
from django.conf import settings

from will_common.utils.encryptutils import encrpt_msg

push_url = settings.PUSH_URL


def push_msg(users, msg):
    for user in users:
        push_msg_tophone(user.phone, msg)
    return 'push success'


def push_msg_tophone(phone, msg):
    # logging.info('alert happening: %s : %s' % (phone, msg))
    # headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"}
    # r = requests.get(push_url % (encrpt_msg(phone), encrpt_msg(msg)), headers=headers)
    # print r.headers
    # print r.content

    # data = {'mobileNo': 'PWy9rKUlzFLGO8Ry6v368w==', 'content': 'ZDvap/iSBk3oBD9Danq7LMphVSFwYhHE7CMnTkJxfagZXyEtfd87fYVuZR3lAuWs'}
    # header = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}
    #
    # rep = requests.get(url='https://advert.jianlc.com/sendMessage.shtml', data=data, headers=header, verify=True)
    # print rep.content

    msg_ = push_url % (encrpt_msg(phone), encrpt_msg(msg))
    print('mmmmmmmmmmm : %s ' % msg_)
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
