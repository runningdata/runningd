echo "new one `date +%Y%m%d`"
hdfs dfs -du -h /apps/hive | grep warehouse
hdfs dfs -du -h /apps/hive/warehouse
hdfs dfs -du -h /log | grep statistics
