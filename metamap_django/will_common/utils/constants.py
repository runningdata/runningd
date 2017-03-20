# -*- coding: utf-8 -*
'''
created by will
'''
DATE_FORMAT = "%Y-%m-%d"
DATEKEY_FORMAT = "%Y%m%d"

# For database usage
MSG_NO_DATA = 'NO_DATA'

# For dqms
DATASRC_TYPE_HIVE = 'hive'
DATASRC_TYPE_MYSQL = 'mysql'
ALERT_MSG = u' %s 质检任务  质检用例  规则 %s   %s   %s 规则验证失败  期望值域 %d to %d 实际值 %d'

DATASRC_TYPE_MYSQL_DB = 'dqms_check'

# For metamap
AZKABAN_BASE_LOCATION = "/tmp/"
AZKABAN_SCRIPT_LOCATION = "/var/azkaban-metamap/"
TMP_SCRIPT_LOCATION = "/var/metamap-tmp/"
TMP_EXPORT_FILE_LOCATION = "/server/metamapfiles/"

# 调度时间
CRON_EVERY_WEEK = '0 9 0 * *'
CRON_EVERY_MONTH = '* * * * *'
CRON_EVERY_SEASON = '* * * * *'
CRON_NAME_LIST = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')

# 默认每个页面的size
DEFAULT_PAGE_SIEZE = 7
