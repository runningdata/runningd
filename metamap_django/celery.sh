celery multi start will -A metamap \
 --pidfile="/var/run/celery/%n.pid" \
  --logfile="/var/log/celery/%n.log" \
  --loglevel=info