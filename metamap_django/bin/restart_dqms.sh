#! /bin/bash



## 检查当前进程中是否还有dqms的gunicorn进程活着
function check_gunicorn() {
    lines=`ps -ef | grep dqms_settings | grep -c  /server/xstorm/bin/gunicorn`
    if [[ $lines > 1 ]]; then
        echo "${lines} gunicorns still running..."
        ps -ef |grep dqms_settings
        return ${lines}
    else
        echo "All gunicorns has been killed"
        return 0
    fi
}


#################################
###  1. pull最新代码           ####
#################################

cd /usr/local/will/metamap \
    && git pull

#################################
###  2. 停止所有gunicorn进程   ####
#################################
pid=`ps -ef | grep gunicorn | grep dqms_settings | awk '{if($3 == '1') print $2}'`
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


######################################
###  3. 使用virtualenv启动gunicorn ####
######################################

cd /usr/local/will/metamap/metamap_django
/server/xstorm/bin/python \
    /server/xstorm/bin/gunicorn \
    metamap_django.wsgi:application \
     -c dqms_settings.py
echo "##########   log  ############"
sleep 3s
tail -20 /tmp/dqms_gunicorn_error.log