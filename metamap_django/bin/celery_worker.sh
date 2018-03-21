#! /bin/bash


if [ $# != 5 ];then
    echo "##########################################################"
    echo "Usage celery_worker.sh {target} {app_name} {queue_name} {concurrency} {command}"
    echo "##########################################################"
    exit 1
fi
target=$1
app_name=$2
queue_name=$3
concurrency=$4
command=$5

if [ -z $METAMAP_HOME ];then
    echo "Please set env $METAMAP_HOME first."
    exit 1
else
    echo "METAMAP_HOME is : $METAMAP_HOME"
fi

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

cd $METAMAP_HOME \
    && git pull


cd $METAMAP_HOME/metamap_django



#################################
###  3. 启动新的服务           ####
#################################
function start(){
export C_FORCE_ROOT=true

    /server/xstorm/bin/python manage.py celery multi start ${target} -A ${app_name} \
      -Q ${queue_name} \
      --pidfile="/var/run/celery/%n.pid" \
      --logfile="/var/log/celery/%n.log" \
      --settings=${app_name}.config.prod \
      --concurrency=${concurrency} \
      --loglevel=info
    
    tail -20 /var/log/celery/${target}.log
}


if [ $command == "stop" ];then
    stop
elif [ $command == "start" ];then
    start
elif [ $command == "restart" ];then
    stop
    start
fi

