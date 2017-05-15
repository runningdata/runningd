#! /bin/bash


if [ -z $METAMAP_HOME ];then
    echo "Please set env $METAMAP_HOME first."
    exit 1
else
    echo "METAMAP_HOME is : $METAMAP_HOME"
fi

## 检查当前进程中是否还有celery进程活着
function check() {
    lines=`ps -ef |grep celery | grep -v dqms | grep will_jar | wc -l`
    if [[ $lines > 0 ]]; then
        echo "${lines}: celery ${1} still running..."
        ps -ef |grep celery | grep will_jar | grep ${1}
        return ${lines}
    else
        echo "metamap celery ${1} has been killed"
        return 0
    fi
}

###  停止所有celery指定进程
function stop() {
    pid=`ps -ef | grep celery |  grep -v dqms | grep will_jar | awk '{if($3 == '1') print $2}'`
    if [[ $pid > 0 ]]; then
        echo "Got ${1} master pid : ${pid}"
        kill $pid
        check $1
        status=$?
        echo "got status....${status}"
        sleep 10s
        until [ $status -eq 0 ]
        do
            check $1
            status=$?
            sleep 5s
        done
    else
        echo "Cannot find master pid for ${1}"
    fi
}

#################################
###  1. pull最新代码           ####
#################################

cd $METAMAP_HOME \
    && git pull


cd $METAMAP_HOME/metamap_django


#################################
###  2. 关闭正在运行的服务           ####
#################################
stop worker


#################################
###  3. 启动新的服务           ####
#################################
export C_FORCE_ROOT=true

/server/xstorm/bin/python manage.py celery multi start will_jar -Q running_jar -A metamap \
 --pidfile="/var/run/celery/%n.pid" \
  --logfile="/var/log/celery/%n.log" \
  --settings=metamap.config.prod \
  --concurrency=2 \
  --loglevel=info

tail -20 /var/log/celery/will_jar.log

