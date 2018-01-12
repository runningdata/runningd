#!/bin/bash

if [ $# != 1 ];then
    echo "##########################################################"
    echo "Usage celery_start.sh {command}[start|stop|restart]"
    echo "##########################################################"
    exit 1
fi

cd $METAMAP_HOME/metamap_django

function handle_worker() {
    # celery_worker.sh {target} {app_name} {queue_name} {concurrency} {command}

    command=$1
    # 运行jar包的任务
    sh bin/celery_worker.sh will_jar metamap running_jar 2 ${command}

    # 运行spark的任务
    sh bin/celery_worker.sh will_spark metamap cron_spark 2 ${command}

    # 运行即时调度的任务
    sh bin/celery_worker.sh will_metamap metamap celery 4 ${command}

    # 运行定时ETL调度的任务
    sh bin/celery_worker.sh will_cron metamap cron_tsk 4 ${command}

    # 运行dqms调度的任务
    sh bin/celery_worker.sh will_dqms dqms dqms 2 ${command}

    # 运行定时alert的任务
    sh bin/celery_worker.sh will_alert running_alert running_alert 2 ${command}
}


function status(){
    for s in `ls /var/run/celery/`;
        echo $s is running
    end for
}

if [ $1 == "status" ];then
    status
else
    handle_worker $1
fi
