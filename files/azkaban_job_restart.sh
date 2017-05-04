
project_name=$1
project_zip_file=/tmp/${project_name}.zip

tmp_output=/tmp/${project_name}_tmp_log
host=10.2.19.62:8081
metamap_host=10.2.19.62:8088
project_desc=${project_name}_schedule


echo "project_name is ${project_name}"
echo "project_zip_file is ${project_zip_file}"
echo "azkaban host is ${host}"

# 获取session id
curl -k -X POST --data "username=azkaban&password=15yinker@bj&action=login" http://${host} > ${tmp_output}
echo result is `cat ${tmp_output}`
session_id=`cat ${tmp_output} | grep session | awk -F\" '!/[{}]/{print $(NF-1)}'`
echo "we got session id : $session_id"

### 创建project
echo "project name is ${project_name}"
curl -k -X POST --data "session.id=${session_id}&name=${project_name}&description=${project_desc}" http://${host}/manager?action=create > ${tmp_output}
status=`cat ${tmp_output} | JSON.sh -b| grep status | awk '{print($2)}'`
if [ $status != '"success"' ]; then
        echo "error happends when creting project ${project_name}. status is ${status}"
        exit 1
fi
echo "project ${project_name} has been created successfully."

# 上传zip文件到指定project
curl -k -i -H "Content-Type: multipart/mixed" -X POST --form "session.id=${session_id}" --form 'ajax=upload' --form "file=@${project_zip_file}" --form "project=${project_name}" http://${host}/manager?ajax=upload > ${tmp_output}
status=`cat ${tmp_output} | awk '{if(index($0,"error") > 0) print("error")}'`
if [[ $status = "error" ]]; then
        echo "error happends when uploading project ${project_name}. status is ${status}"
        exit 1
fi
echo "uploading project ${project_name} successfully"

# 遍历执行project下的flow
curl -k --get --data "session.id=${session_id}&ajax=fetchprojectflows&project=${project_name}" http://${host}/manager > ${tmp_output}
for flow in `cat ${tmp_output} |  JSON.sh -b | grep flowId |  awk '{gsub("\"","",$2);print($2)}'`
do
        echo "flow is $flow, ready to execute"
        curl -k --get --data "session.id=${session_id}" --data 'ajax=executeFlow' --data "project=${project_name}" --data "flow=${flow}" --data "failureAction=finishPossible" http://${host}/executor >${tmp_output}${flow}
        execid=`cat ${tmp_output}${flow} | JSON.sh -b| grep execid | awk '{print($2)}'`
        echo "got execid : ${execid}"
echo "$flow execution done"
done
echo "all flows for project ${project_name} has been executed"
rm -vf ${tmp_output}

