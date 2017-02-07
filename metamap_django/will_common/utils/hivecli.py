import logging

import pyhs2, json
import re
from django.conf import settings
from pyhs2.error import Pyhs2Exception

from will_common.utils import constants
from will_common.utils import djtemplates

logger = logging.getLogger('django')


def getTbls(etl):
    sql = djtemplates.get_etl_sql(etl)
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
                print(' got deps : %s ' % deps)
                tables_ = deps['input_tables']
                for tbl in tables_:
                    result.add(tbl['tablename'])
                logger.info('analyse sql done ')
    except Pyhs2Exception, e:
        raise Exception('sql is %s,\n<br> error is %s' % (sql, e))
    return result


def execute(sql):
    result = dict()
    try:
        with pyhs2.connect(host=settings.HIVE_SERVER['host'],
                           port=settings.HIVE_SERVER['port'],
                           authMechanism="PLAIN",
                           user=settings.HIVE_SERVER['user'],
                           password=settings.HIVE_SERVER['password'],
                           database='default') as conn:
            # with pyhs2.connect(host='10.1.5.63',
            #                    port='10000',
            #                    authMechanism="PLAIN",
            #                    user='hdfs',
            #                    password='',
            #                    database='default') as conn:
            with conn.cursor() as cur:
                logger.info('clean sql is %s ' % sql)
                # Execute query
                cur.execute(sql)

                # Fetch table results
                schema = cur.getSchema()
                fetchall = cur.fetchall()
                if len(fetchall) == 0:
                    cur.close()
                    return
                row = fetchall[0]
                cur.close()
                for col in schema:
                    index = schema.index(col)
                    result[col['columnName']] = row[index]
                print result
                return result
    except Pyhs2Exception, e:
        raise Exception('sql is %s,\n<br> error is %s' % (sql, e))


if __name__ == '__main__':
    # heh = getTbls("insert into xxsx select * from batting full join jlc.bank_card")
    heh = execute("select create_date as dat, userid from wind_test.topic_user limit 1")
    print heh
