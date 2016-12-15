#!/bin/bash

etl_tmp=/tmp/etl_tmp_log
host=10.0.1.62:8081
metamap_host=10.0.1.62:8088
project_desc=daily_schedule


# 调用生成job的任务，返回任务名称或者失败信息
function get_jobs() {
    curl -X GET http://${metamap_host}/metamap/etls/generate_job_dag/0/ > ${etl_tmp}
    filename=`cat ${etl_tmp}`
    if [ ${#filename} -ne 14 ]; then
        echo "error happends when generate Job Scripts. ori_filename is ${filename}"
        echo "length is ${#filename}"
        failed_num=`expr $failed_num + 1`
        echo "failed for ${failed_num} times"
        if [ $failed_num -eq 30 ]; then
                exit 1
        fi
        sleep 10m
        get_jobs
    fi
}

get_jobs

project_name=etl_${filename}
project_zip_file=/tmp/${filename}.zip

echo "project_name is ${project_name}"
echo "project_zip_file is ${project_zip_file}"
echo "azkaban host is ${host}"

# 获取session id
curl -k -X POST --data "username=azkaban&password=azkaban&action=login" http://${host} > ${etl_tmp}
echo result is `cat ${etl_tmp}`
session_id=`cat ${etl_tmp} | grep session | awk -F\" '!/[{}]/{print $(NF-1)}'`
echo "we got session id : $session_id"

### 创建project
echo "project name is ${project_name}"
curl -k -X POST --data "session.id=${session_id}&name=${project_name}&description=${project_desc}" http://${host}/manager?action=create > ${etl_tmp}
status=`cat ${etl_tmp} | JSON.sh -b| grep status | awk '{print($2)}'` 
if [ $status != '"success"' ]; then
        echo "error happends when creting project ${project_name}. status is ${status}"
	exit 1
fi
echo "project ${project_name} has been created successfully."

# 上传zip文件到指定project
curl -k -i -H "Content-Type: multipart/mixed" -X POST --form "session.id=${session_id}" --form 'ajax=upload' --form "file=@${project_zip_file}" --form "project=${project_name}" http://${host}/manager?ajax=upload > ${etl_tmp}
status=`cat ${etl_tmp} | awk '{if(index($0,"error") > 0) print("error")}'`
if [[ $status = "error" ]]; then
        echo "error happends when uploading project ${project_name}. status is ${status}"
        exit 1
fi
echo "uploading project ${project_name} successfully"

# 
# 阻塞检察某个execution的进度
#
function check_exec_status(){
	execid=$1
	sleep 1h
	#查看前execution的执行状态，完成后退出
	status=RUNNING
	until [ $status == '"SUCCEEDED"' ]
	do
    		curl -k --get --data "session.id=${session_id}&ajax=fetchexecflowupdate&execid=${execid}&lastUpdateTime=-1" http://${host}/executor > ${etl_tmp}
    		status=`cat ${etl_tmp} | JSON.sh -b| grep status | grep -v node | awk '{print($2)}'`
		if [ $status == '"KILLED"' ]; then
			echo "${execid} has been killed."
			break
		elif [ $status == '"FAILED"' ]; then
                        echo "${execid} has been failed."
                        break
		fi
    		echo "${execid} not yet..." `cat ${etl_tmp}`
		sleep 10m	
	done
}

# 遍历执行project下的flow
curl -k --get --data "session.id=${session_id}&ajax=fetchprojectflows&project=${project_name}" http://${host}/manager > ${etl_tmp}
for flow in `cat ${etl_tmp} |  JSON.sh -b | grep flowId |  awk '{gsub("\"","",$2);print($2)}'`
do
        echo "flow is $flow, ready to execute"
        curl -k --get --data "session.id=${session_id}" --data 'ajax=executeFlow' --data "project=${project_name}" --data "flow=${flow}" --data "failureAction=finishPossible" http://${host}/executor >${etl_tmp}${flow}
        execid=`cat ${etl_tmp}${flow} | JSON.sh -b| grep execid | awk '{print($2)}'`
	echo "got execid : ${execid}"
	check_exec_status ${execid}
echo "$flow execution done"
done
echo "all flows for project ${project_name} has been executed"
