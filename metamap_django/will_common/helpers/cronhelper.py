# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import re

from will_common.utils.constants import CRON_NAME_LIST


def cron_from_str(str):
    p = re.compile('\s')
    return p.split(str.strip())

if __name__ == '__main__':
    a = cron_from_str('3/* * * * *')
    result = zip(CRON_NAME_LIST, a, a)
    print type(result)
    for k, v, x in result:
        print k, v, x