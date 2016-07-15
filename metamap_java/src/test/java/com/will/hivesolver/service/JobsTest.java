package com.will.hivesolver.service;

import com.will.hivesolver.entity.ETL;
import com.will.hivesolver.entity.Node;
import com.will.hivesolver.entity.TblBlood;
import com.will.hivesolver.util.JsonUtil;
import com.will.hivesolver.util.PropertiesUtils;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.hadoop.hive.metastore.api.MetaException;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import java.util.*;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/applicationContext.xml")
public class JobsTest {
    private static Logger log = LoggerFactory.getLogger(JobsTest.class);

    @Autowired
    private ETLService etlService;

    @Test
    public void testinsertEtl() {
        System.out.println(etlService.getExecutionById(1));
    }

    @Test
    public void testRepGetOne() {
        System.out.println(etlService.getETLBId(1));
    }


}
