import logging

import pyhs2, json
import re
from django.conf import settings
from django.template import Context
from django.template.backends.django import Template
from pyhs2.error import Pyhs2Exception

from metamap.helpers import etlhelper
logger = logging.getLogger('django')

def getTbls(etl):
    sql = etlhelper.get_etl_sql(etl)
    result = set()
    try:
        with pyhs2.connect(host=settings.HIVE_SERVER['host'],
                           port=settings.HIVE_SERVER['port'],
                           authMechanism="PLAIN",
                           user=settings.HIVE_SERVER['user'],
                           password=settings.HIVE_SERVER['password'],
                           database='default') as conn:
            with conn.cursor() as cur:

                sql = sql[sql.lower().index('select'):]
                matchObj = re.match(r'.*,(reflect\(.*\)).*,.*', sql, re.I | re.S)
                if matchObj:
                    sql = sql.replace(matchObj.group(1), '-999')

                logger.info('clean sql is %s ' % sql)
                # Execute query
                cur.execute("explain dependency " + sql)

                # Fetch table results
                deps = json.loads(cur.fetchone()[0])
                tables_ = deps['input_tables']
                for tbl in tables_:
                    result.add(tbl['tablename'])
                logger.info('analyse sql done ')
    except Pyhs2Exception, e:
        raise Exception('sql is %s,\n<br> error is %s' % (sql, e))
    return result


if __name__ == '__main__':
    heh = getTbls("insert into xxsx select * from batting full join jlc.bank_card")
    print heh
