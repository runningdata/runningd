#! /bin/bash

export C_FORCE_ROOT=true

celery multi start will -A metamap \
 --pidfile="/var/run/celery/%n.pid" \
  --logfile="/var/log/celery/%n.log" \
  --loglevel=info

tail -20 /var/log/celery/will.log

celery beat --loglevel=info --logfile="/var/log/celery/beat.log" \
 --pidfile="/var/run/celery/beat.pid" \
 --settings=metamap.config.prod \
 --detach


tail -20 /var/log/celery/beat.log