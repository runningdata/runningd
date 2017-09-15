#!/bin/bash
if [ $# -ne 2 ];then
echo "Usage: azkaban_daily_m2h.sh {project_name} {group_name}"
exit 0
fi

METAMAP_HOME=/server/metamap
project_name=$1
group_name=$2
tmp_output=/tmp/${project_name}_tmp_log
host=10.2.19.62:8081
metamap_host=10.2.19.62:8088


# 获取session id
curl -k -X POST --data "username=azkaban&password=15yinker@bj&action=login" http://${host} > ${tmp_output}
echo result is `cat ${tmp_output}`
session_id=`cat ${tmp_output} | grep session | awk -F\" '!/[{}]/{print $(NF-1)}'`
echo "we got session id : $session_id"


# 
# 阻塞检察某个execution的进度
#
function check_exec_status(){
	execid=$1
	sleep 2m
	#查看前execution的执行状态，完成后退出
	status=RUNNING
	until [ $status == '"SUCCEEDED"' ]
	do
		echo execid is ${execid}
                /server/xstorm/bin/python ${METAMAP_HOME}/files/azkaban_job_checker.py  --execid ${execid}  > ${tmp_output}
                cat ${tmp_output}
                status=`cat ${tmp_output} | grep r10r | awk '{print($2)}'`
                if [ $status == 'KILLED' ]; then
                        echo "${execid} has been killed."
                        curl -X GET http://${metamap_host}/metamap/ops/push_msg/?group=${group_name}\&status=${status}\&prjname=${project_name}
                        break
                elif [ $status == 'FAILED' ]; then
                        echo "${execid} has been failed."
                        curl -X GET http://${metamap_host}/metamap/ops/push_msg/?group=${group_name}\&status=${status}\&prjname=${project_name}
                        break
                elif [ $status == 'SUCCEEDED' ]; then
                        echo "${execid} has been SUCCEEDED."
                        break
                fi
                execid=`cat ${tmp_output} | grep i10d | awk '{print($2)}'`
		sleep 2m	
	done
}

# 遍历执行project下的flow
curl -k --get --data "session.id=${session_id}&ajax=fetchprojectflows&project=${project_name}" http://${host}/manager > ${tmp_output}
cat ${tmp_output}
for flow in `cat ${tmp_output} |  JSON.sh -b | grep flowId |  awk '{gsub("\"","",$2);print($2)}'`
do
        echo "flow is $flow, ready to execute"
        curl -k --get --data "session.id=${session_id}" --data 'ajax=executeFlow' --data "project=${project_name}" --data "flow=${flow}" --data "failureAction=finishPossible" http://${host}/executor >${tmp_output}${flow}
        execid=`cat ${tmp_output}${flow} | JSON.sh -b| grep execid | awk '{print($2)}'`
	echo "got execid : ${execid}"
	check_exec_status ${execid}
echo "$flow execution done"
done
echo "all flows for project ${project_name} has been executed"
rm -vf ${tmp_output}
