# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''


def enum(*seq, **named):
    enums = dict(zip(seq, range(len(seq))), **named)
    return type('Enum', (), enums)


EXECUTION_STATUS = enum('RUNNING', 'DONE', 'FAILED')