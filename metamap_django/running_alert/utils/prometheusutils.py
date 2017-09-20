import requests
from django.conf import settings


def get_spark_app():
    apps = set()
    res = requests.get(settings.SPARK_EXPORTER_HOST)
    # res = requests.get('http://10.1.5.190:880/metrics')
    if res.status_code == 200:
        for line in res.content.split('\n'):
            if 'spark_up' in line:
                ee = line.split(' ')[0]
                kv = ee.replace('spark_up{app_name="', '').replace('"}', '')
    return apps
