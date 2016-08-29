#! /bin/bash
celery multi start will -A metamap \
 --pidfile="/var/run/celery/%n.pid" \
  --logfile="/var/log/celery/%n.log" \
  --loglevel=info

tail -20 /var/log/celery/will.log