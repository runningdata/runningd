# -*- coding: utf-8 -*
import logging
import urllib2

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
                v = ''.join(v).strip()
                print k ,v
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


def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
    httpHandler = urllib2.HTTPHandler(debuglevel=0)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=0)
    opener = urllib2.build_opener(httpHandler, httpsHandler)
    urllib2.install_opener(opener)
    resp = urllib2.urlopen(req)
    if resp.getcode() == 200:
        return resp.read()
    else:
        return 'error'


def jlc_auth(user, sid):
    url = 'http://xlightning.jianlc.com/valsession?username=%s&sessionid=%s' % (user, sid)
    return get_url(url)
