# -*- coding: utf-8 -*
import logging

'''
http的一些常用的工具方法
'''


def post2obj(obj, post, *excludes):
    '''
    将post里的参数对应copy到obj里，主要是方便http接口直接使用obj进行操作
    :param obj:
    :param post:
    :return:
    '''
    dic = dict(post)
    for k, v in dic.iteritems():
        if k not in excludes:
            if hasattr(obj, k):
                v = ''.join(v)
                setattr(obj, k, v)
    logging.info("post params has been copied to  obj -> %s" % obj)


def get2obj(obj, get, *excludes):
    '''
    将get里的参数对应copy到obj里，主要是方便http接口直接使用obj进行操作
    :param obj:
    :param post:
    :return:
    '''
    dic = dict(get)
    for k, v in dic.iteritems():
        if k not in excludes:
            if hasattr(obj, k):
                v = ''.join(v)
                setattr(obj, k, v)
    logging.info("get params has been copied to  obj -> %s" % obj)
