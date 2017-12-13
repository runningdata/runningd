# -*- coding: utf-8 -*
import djcelery

djcelery.setup_loader()
from init_config import result

# Celery Beat 设置
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_TASK_SOFT_TIME_LIMIT = 3600
BROKER_URL = 'redis://{celery_host}:{celery_port}'.format(celery_host=result['CELERY_REDIS_HOST'],
                                                          celery_port=result['CELERY_REDIS_PORT'])
CELERY_ROUTES = {
    'dqms.tasks.exec_dqms': {
        'queue': 'dqms',
    },
    'dqms.tasks.run_case': {
        'queue': 'dqms',
    },
}
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_REDIS_HOST = result['CELERY_REDIS_HOST']
CELERY_REDIS_PORT = result['CELERY_REDIS_PORT']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE = 'UTC'
# CELERY_ENABLE_UTC = True
# CELERY_IMPORTS = ("metamap.taske",)
