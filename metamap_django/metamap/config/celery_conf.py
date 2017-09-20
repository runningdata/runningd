# -*- coding: utf-8 -*
import djcelery

djcelery.setup_loader()

# Celery Beat 设置
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_TASK_SOFT_TIME_LIMIT = 3600
# BROKER_URL = 'redis://datanode08.yinker.com:6379'
BROKER_URL = 'redis://10.2.19.113:6480'

CELERY_ROUTES = {
    'metamap.tasks.exec_jar': {
        'queue': 'running_jar',
    },
    'running_alert.tasks.*': {
        'queue': 'running_alert',
    },
}
# CELERY_ROUTES = ([
#                      {'metamap.tasks.exec_jar': {
#                          'queue': 'running_jar',
#                      }},
#                      {'web.tasks.*', {'queue': 'web'}},
#                  ],)

CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_REDIS_HOST = '10.2.19.113'
CELERY_REDIS_PORT = '6480'
# CELERY_REDIS_HOST = 'datanode08.yinker.com'
# CELERY_REDIS_PORT = '6379'
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE = 'UTC'
# CELERY_ENABLE_UTC = True
# CELERY_IMPORTS = ("metamap.taske",)
