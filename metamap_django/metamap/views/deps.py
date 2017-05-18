# -*- coding: utf-8 -*
import logging
import os
import traceback

from django.http import HttpResponse

from metamap.helpers import etlhelper
from metamap.models import ExecBlood, ExecObj, SqoopHive2Mysql, SqoopMysql2Hive
from will_common.utils import dateutils
from will_common.utils import ziputils
from will_common.utils.constants import AZKABAN_BASE_LOCATION, AZKABAN_SCRIPT_LOCATION

logger = logging.getLogger('django')

def generate_job_dag_v2(request, schedule):
    '''
    抽取所有有效的ETL,生成azkaban调度文件
    :param request:
    :return:
    '''
    try:
        done_blood = set()
        done_leaf = set()
        folder = 'generate_job_dag_v2-' + dateutils.now_datetime()
        leafs = ExecBlood.objects.raw("SELECT 1 as id, a.* FROM "
                                     "(select DISTINCT child_id FROM metamap_etlblood) a "
                                     "join ("
                                     "select rel_id from metamap_willdependencytask where `schedule` = " + schedule + " and valid=1 and type = 100 "
                                                                                                                      ") b "
                                                                                                                      "on a.child_id = b.rel_id "
                                                                                                                      "left outer join ("
                                                                                                                      "SELECT DISTINCT parent_id from metamap_etlblood ) c "
                                                                                                                      "on a.child_id = c.parent_id "
                                                                                                                      "where c.parent_id is NULL")

        final_deps = set()
        leaves = set()
        for leaf in leafs:
            leaf_etl = ExecObj.objects.get(pk=leaf.child_id)
            if leaf_etl.type == 3:
                # H2M的名字不能是hive表了，这样就跟H2H的重复了
                etl = SqoopHive2Mysql.objects.get(pk=leaf_etl.rel_id)
                tbl_name = etl.hive_meta.meta + '@' + etl.hive_tbl
                job_name = 'export_' + tbl_name
                final_deps.add(job_name)
            elif leaf_etl.type == 4:
                etl = SqoopMysql2Hive.objects.get(pk=leaf_etl.rel_id)
                tbl_name = etl.hive_meta.meta + '@' + etl.mysql_tbl
                job_name = 'import_' + tbl_name
                final_deps.add(job_name)
            else:
                final_deps.add(leaf_etl.name)
            leaves.add(leaf_etl.id)

        os.mkdir(AZKABAN_BASE_LOCATION + folder)
        os.mkdir(AZKABAN_SCRIPT_LOCATION + folder)

        etlhelper.load_nodes_v2(leaves, folder, done_blood, done_leaf, schedule)

        etlhelper.generate_job_file_v2(ExecObj(name='etl_v2_done_' + folder), final_deps, folder, folder)
        # PushUtils.push_msg_tophone(encryptutils.decrpt_msg(settings.ADMIN_PHONE),
        #                            '%d etls generated ' % len(done_blood))
        ziputils.zip_dir(AZKABAN_BASE_LOCATION + folder)
        return HttpResponse(folder)
    except Exception, e:
        logger.error('error : %s ' % e)
        logger.error('traceback is : %s ' % traceback.format_exc())
        return HttpResponse('error')
