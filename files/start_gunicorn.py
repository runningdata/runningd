#!/bin/bash
NAME="metamap" # application名称
DJANGODIR=/usr/local/metamap/metamap_django # Django project目录
USER=root # 使用什么用户运行
GROUP=root # 使用什么用户组运行
NUM_WORKERS=3 # Gunicorn程序启动多少个并发worker
DJANGO_SETTINGS_MODULE=settings.py # django要使用的settings文件

echo "Starting $NAME"

# Activate the virtual environment
# 激活virtualenv环境
cd $DJANGODIR
source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# 创建运行的文件夹
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# 启动程序
gunicorn metamap_django.wsgi:application -c gunicorn_settings.py
