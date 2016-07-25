import pyhs2, json

def getTbls(sql):
    result = set()
    with pyhs2.connect(host='10.1.5.80',
                       port=10000,
                       authMechanism="PLAIN",
                       user='hdfs',
                       password='test',
                       database='default') as conn:
        with conn.cursor() as cur:
            sql = sql[sql.index('select'):]
            # Execute query
            cur.execute("explain dependency " + sql)

            # Fetch table results
            deps = json.loads(cur.fetchone()[0])
            tables_ = deps['input_tables']
            for tbl in  tables_:
                result.add(tbl['tablename'])
    return result

if __name__ == '__main__':
    heh = getTbls("insert into xxsx select * from batting full join jlc.bank_card")
    print heh