package com.will.hivesolver.service;

import java.util.List;
import java.util.Set;

import javax.annotation.Resource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.will.hivesolver.HiveJdbcClient;
import com.will.hivesolver.dao.IETLDao;
import com.will.hivesolver.dao.ITblBloodDao;
import com.will.hivesolver.entity.ETL;
import com.will.hivesolver.entity.TblBlood;

@Service
public class TblBloodService {

    private static Logger log = LoggerFactory.getLogger(TblBloodService.class);

    @Resource(name = "tblBloodDao")
    private ITblBloodDao tblBloodDao;
    
    @Resource(name = "etlDao")
    private IETLDao etlDao;

    public  List<TblBlood> allTblBlood() {
        return tblBloodDao.selectAll();
    }
    
    /**
     * 
     */
    public  String resolveDependency() {
        long start = System.currentTimeMillis();
        List<ETL> allETL = etlDao.selectAllValidETL();
        for (ETL etl : allETL) {
            log.info(">>> sql to be parsed : " + etl.getQuery());
            Set<String> parents = HiveJdbcClient.get(etl.getQuery());
            TblBlood blood = null;
            for (String parent : parents) {
                blood = new TblBlood();
                blood.setParentTbl(parent);
                blood.setRelatedEtlId(etl.getId());
                blood.setTblName(etl.getMeta() + "@" + etl.getTblName());
                blood.setUtime(System.currentTimeMillis()/1000);
                tblBloodDao.insertOne(blood);
            }
            log.info(">>> parse done for : " + etl.getQuery());
        }
        long time = (System.currentTimeMillis() - start) / 1000;
        log.info(allETL.size() + " etls has been parsed for " + time + " seconds" );
        return allETL.size() + " etls has been parsed for " + time + " seconds" ;
    }
    
}
