# -*- coding: utf-8 -*
import djcelery

djcelery.setup_loader()
from init_config import result

# Celery Beat 设置
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_TASK_SOFT_TIME_LIMIT = result.get('CELERYD_TASK_SOFT_TIME_LIMIT', 1800)
BROKER_URL = 'redis://{celery_host}:{celery_port}'.format(celery_host=result.get('CELERY_REDIS_HOST', '10.2.19.113'),
                                                          celery_port=result.get('CELERY_REDIS_PORT', '6480'))

CELERY_ROUTES = {
    'metamap.tasks.exec_jar': {
        'queue': 'running_jar',
    },
    'running_alert.tasks.check_new_spark': {
        'queue': 'running_alert',
    },
    'running_alert.tasks.check_disabled_spark': {
        'queue': 'running_alert',
    },
    'running_alert.tasks.check_new_jmx': {
        'queue': 'running_alert',
    },
    'running_alert.tasks.check_disabled_jmx': {
        'queue': 'running_alert',
    },
}

CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_REDIS_HOST = result.get('CELERY_REDIS_HOST', '10.2.19.113')
CELERY_REDIS_PORT = result.get('CELERY_REDIS_PORT', '6480')
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE = 'UTC'
# CELERY_ENABLE_UTC = True
# CELERY_IMPORTS = ("metamap.taske",)
