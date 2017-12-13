# -*- coding: utf-8 -*
import djcelery

djcelery.setup_loader()

# Celery Beat 设置
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_TASK_SOFT_TIME_LIMIT = 3600
BROKER_URL = 'redis://10.2.19.113:6480'
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ROUTES = {
    'running_alert.tasks.check_new_spark': {
        'queue': 'running_alert',
    },
}

CELERY_REDIS_HOST = '10.2.19.113'
CELERY_REDIS_PORT = '6480'
# CELERY_REDIS_PORT = '6379'
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE = 'UTC'
# CELERY_ENABLE_UTC = True
# CELERY_IMPORTS = ("metamap.taske",)