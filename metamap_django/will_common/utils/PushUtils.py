# -*- coding: utf-8 -*
import logging
import urllib2

import requests

from metamap_django import settings
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

    data = {'mobileNo': 'PWy9rKUlzFLGO8Ry6v368w==', 'content': 'ZDvap/iSBk3oBD9Danq7LMphVSFwYhHE7CMnTkJxfagZXyEtfd87fYVuZR3lAuWs'}
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

    rep = requests.get(url='https://advert.jianlc.com/sendMessage.shtml', data=data, headers=header, verify=True)
    print rep.content

    # req = urllib2.Request(
    #     push_url % (encrpt_msg(phone), encrpt_msg(msg)), headers=headers)
    # req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    # req.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
    # req.add_header('Upgrade-Insecure-Requests', 1)
    # # req.add_header('User-Agent',
    # #                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
    # print('header : %s' % req.get_header('User-Agent'))
    # try:
    #     resp = urllib2.urlopen(req)
    #     if resp.getcode() == 200:
    #         print resp.read()
    #         return 'push phone success'
    #     else:
    #         return 'error', resp.read()
    # except urllib2.URLError, e:
    #     return e.reason
