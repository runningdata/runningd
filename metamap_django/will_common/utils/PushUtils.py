# -*- coding: utf-8 -*
import logging


def push_msg(users, msg):
    for user in users:
        print(msg, user.phone)
    return 'push success'

def push_msg_tophone(phone, msg):
    print(msg, phone)
    return 'push phone success'