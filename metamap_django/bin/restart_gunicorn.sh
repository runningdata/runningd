#! /bin/bash

if [ -z $METAMAP_HOME ];then
    echo "Please set env $METAMAP_HOME first."
    exit 1
else
    echo "METAMAP_HOME is : $METAMAP_HOME"
fi


## 检查当前进程中是否还有gunicorn进程活着
function check_gunicorn() {
    lines=`ps -ef |grep -c  $METAMAP_HOME_virenv/bin/gunicorn`
    if [[ $lines > 1 ]]; then
        echo "${lines} gunicorns still running..."
        ps -ef |grep -c  $METAMAP_HOME_virenv/bin/gunicorn
        return ${lines}
    else
        echo "All gunicorns has been killed"
        return 0
    fi
}


#################################
###  1. pull最新代码           ####
#################################

cd $METAMAP_HOME \
    && git pull

#################################
###  2. 停止所有gunicorn进程   ####
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


######################################
###  3. 使用virtualenv启动gunicorn ####
######################################

cd $METAMAP_HOME/metamap_django
$METAMAP_HOME_virenv/bin/python \
    $METAMAP_HOME_virenv/bin/gunicorn \
    metamap_django.wsgi:application \
     -c gunicorn_settings.py
echo "##########   log  ############"
sleep 3s
tail -20 /tmp/gunicorn_error.log