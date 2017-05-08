# -*- coding: utf-8 -*
import json
from operator import itemgetter

import redis
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from kombu.serialization import pickle

from will_common.models import WillDependencyTask

pool = redis.ConnectionPool(host=settings.CELERY_REDIS_HOST, port=settings.CELERY_REDIS_PORT, max_connections=2)


def get_keys():
    r = redis.StrictRedis(connection_pool=pool)
    return [key for key in r.keys() if '_' not in key and 'unack' not in key]

def get_dict(key):
    messages = dict()
    r = redis.StrictRedis(connection_pool=pool)
    if r.exists(key):
        messages = r.hgetall(key)
    return messages

def get_queue_count(queue_name, count=-1):
    r = redis.StrictRedis(connection_pool=pool)
    if r.exists(queue_name):
        messages = r.lrange(queue_name, 0, count)
    return len(messages)

def get_queue_info(queue_name, count=-1):
    r = redis.StrictRedis(connection_pool=pool)
    count_dict = {}
    task_set = list()
    if r.exists(queue_name):
        messages = r.lrange(queue_name, 0, count)
        for m in messages:
            m = json.loads(m)
            body_encoding = m['properties']['body_encoding']
            body = pickle.loads(m['body'].decode(body_encoding))
            task_name = body['task']
            try:
                if 'exec_etl_cli' in task_name:
                    task_set.add(WillDependencyTask.objects.get(pk=int(body['args'][0])).name)
                else:
                    task_set.append(body['args'][0])
            except ObjectDoesNotExist, e:
                print ' args is %s ' % body['args'][0]
            count_dict[task_name] = count_dict.get(task_name, 0) + 1
    list_ = sorted(count_dict.items(), key=itemgetter(1), reverse=True)
    print('queue : %s ' % queue_name)
    print('list is ')
    print(list_)
    print('task_set is ')
    print(task_set)
    return list_, task_set
