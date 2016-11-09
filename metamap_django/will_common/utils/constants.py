# -*- coding: utf-8 -*
'''
created by will
'''
DATE_FORMAT = "%Y-%m-%d"
DATEKEY_FORMAT = "%Y%m%d"
AZKABAN_BASE_LOCATION = "/tmp/"
AZKABAN_SCRIPT_LOCATION = "/var/azkaban-metamap/"
TMP_SCRIPT_LOCATION = "/var/metamap-tmp/"
TMP_EXPORT_FILE_LOCATION = "/var/metamapfiles/"

# 调度时间
CRON_EVERY_WEEK = '0 9 0 * *'
CRON_EVERY_MONTH = '* * * * *'
CRON_EVERY_SEASON = '* * * * *'
CRON_NAME_LIST = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')

# 默认每个页面的size
DEFAULT_PAGE_SIEZE = 7
