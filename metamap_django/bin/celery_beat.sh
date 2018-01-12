#! /bin/bash

target=beat
command=$1
## 检查当前进程中是否还有celery进程活着
function check() {
    pid=$1
    lines=`ps -ef |grep ${pid} | grep ${target} | wc -l`
    if [[ $lines > 0 ]]; then
        echo "${lines}: celery ${1} still running..."
        ps -ef |grep celery | grep ${pid} | grep ${target}
        return ${lines}
    else
        echo "metamap celery ${target} has been killed"
        return 0
    fi
}

###  停止所有celery指定进程
function stop() {
    pid=`cat /var/run/celery/${target}.pid`
    echo $pid
    if [[ $pid > 0 ]]; then
        echo "Got ${target} master pid : ${pid}"
        kill $pid
        check ${pid}
        status=$?
        echo "got status....${status}"
        sleep 10s
        until [ $status -eq 0 ]
        do
            check $pid
            status=$?
            sleep 5s
        done
    else
        echo "Cannot find master pid for ${target}"
    fi

}

#################################
###  1. pull最新代码           ####
#################################

cd ${METAMAP_HOME} \
    && git pull

cd ${METAMAP_HOME}/metamap_django


#################################
###  3. 启动新的服务           ####
#################################
function start(){
    export C_FORCE_ROOT=true

    /server/xstorm/bin/python manage.py celery beat --loglevel=info --logfile="/var/log/celery/beat.log" \
     --pidfile="/var/run/celery/beat.pid" \
     --settings=metamap.config.prod \
     --detach
    tail -20 /var/log/celery/beat.log
}

if [ $command == "stop" ];then
    stop
elif [ $command == "start" ];then
    start
elif [ $command == "restart" ];then
    stop
    start
fi

