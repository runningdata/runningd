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
DATASRC_TYPE_KYLIN = 'kylin'
ALERT_MSG = u'''
        报警
        时间： %s
        质检任务： %s
        质检用例： %s
        规则名称： %s
        期望值域： %d - %d
        实际值 ： %d'''

DATASRC_TYPE_MYSQL_DB = 'dqms_check'
DATASRC_TYPE_KYLIN_DB = ''

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
