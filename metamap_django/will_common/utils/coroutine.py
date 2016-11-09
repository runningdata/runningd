# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
因为不能异步执行，协程的方式pass掉了
created by will 
'''
import time,os


def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        os.system("sh /usr/local/metamap/test.sh > /usr/local/metamap/result.test")
        print('[CONSUMER] Consuming done for  %s...' % n)
        r = '200 OK'


def produce(c):
    c.next()
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()


if __name__ == '__main__':
    c = consumer()
    produce(c)
