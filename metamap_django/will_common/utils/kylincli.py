# -*- coding: utf-8 -*
import requests
import json

# cube_name='olap_basic_cube_v2'
# sql = '''
# select
# sum(inv_amount) as inv_amount,
# sum(invre_amount) as invre_amount,
# sum(redeem_amount) as redeem_amount,
# sum(regular_amount) as regular_amount
# from
# dim_kylin.dim_kylin_bi_temporary
# WHERE create_date>= '2017-05-19'
# and create_date<= '2017-05-19'
# '''
#
# proj = 'olap_bi_temp'
from django.conf import settings


def execute(cube_name, sql):
    try:
        params = {'sql': sql, 'offset': 0, 'limit': '1', 'acceptPartial': False, 'project': cube_name}
        auth_params = (settings.KYLIN_ADMIN_USER, settings.KYLIN_ADMIN_PWD)
        header = {'Content-Type': 'application/json;charset=UTF-8'}
        rep = requests.post(url=settings.KYLIN_REST_URI, json=params, auth=auth_params, headers=header)
        result = {}
        if rep.status_code == 200:
            cols = json.loads(rep.content)['columnMetas']
            colls = [col['name'] for col in cols]
            # types = [col['columnTypeName'] for col in cols]
            vals = json.loads(rep.content)['results'][0]
            result = dict(zip(colls, vals))
            result2 = {k: float(v) for k, v in result.items()}
        else:
            print('Error in kylincli resp status is : %d ' % rep.status_code)
        return result2
    except Exception, e:
        print('Error in kylincli : %s ' % e.message)
        return {}
