#! /bin/bash

## 检查当前进程中是否还有gunicorn进程活着
function check_gunicorn() {
    lines=`ps -ef |grep -c  /server/metamap_virenv/bin/gunicorn`
    if [[ $lines > 1 ]]; then
        echo "${lines} gunicorns still running..."
        ps -ef |grep -c  /server/metamap_virenv/bin/gunicorn
        return ${lines}
    else
        echo "All gunicorns has been killed"
        return 0
    fi
}

#################################
###  1. 停止所有gunicorn进程   ####
#################################
pid=`ps -ef | grep gunicorn | awk '{if($3 == '1') print $2}'`
if [[ $pid > 0 ]]; then
    echo "Got gunicorn master pid : ${pid}"
    kill $pid
    check_gunicorn
    status=$?
    sleep 10s
    until [ $status -eq 0 ]
    do
        check_gunicorn
        status=$?
        sleep 5s
    done
else
    echo "Cannot find master pid for gunicorn"
fi

#################################
###  2. pull最新代码           ####
#################################

cd /server/metamap \
    && git stash \
    && git pull \
    && git stash pop

######################################
###  3. 使用virtualenv启动gunicorn ####
######################################

cd /server/metamap/metamap_django
/server/metamap_virenv/bin/python \
    /server/metamap_virenv/bin/gunicorn \
    metamap_django.wsgi:application \
     -c gunicorn_settings.py
echo "##########   log  ############"
tail -20 /tmp/gunicorn_error.log