# -*- coding: utf-8 -*
import json

from kombu.serialization import pickle


def get_celery_taskname(msg):
    m = json.loads(msg)
    body_encoding = m[0]['properties']['body_encoding']
    body = pickle.loads(m[0]['body'].decode(body_encoding))
    return body


def get_celery_taskname2(msg):
    m = json.loads(msg)
    body_encoding = m['properties']['body_encoding']
    body = pickle.loads(m['body'].decode(body_encoding))
    return body


def readable_celery_arg(arg):
    if isinstance(arg, tuple):
        arg_ = arg[0]
        if isinstance(arg_, int):
            return arg
        if arg_.startswith('hive'):
            return arg_.split("-f")[1]
        else:
            return arg_
    if isinstance(arg, list):
        return arg[0]
    else:
        return arg
