package com.will.hivesolver.service;

import com.will.hivesolver.util.JsonUtil;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

@RunWith(SpringJUnit4ClassRunner.class) 
@ContextConfiguration("/applicationContext.xml")
public class HiveMetaTest {
    private static Logger log = LoggerFactory.getLogger(HiveMetaTest.class);
    
    @Autowired
    private HiveMetaService hiveMetaService;
    
    @Test
    public void testSelectColMeta() throws Exception{
        System.out.println(hiveMetaService.prepareColMeta());
        System.out.println(JsonUtil.writeValueAsString(hiveMetaService.getAll()));
    }
    
    @Test
    public void testDelet() {
        Assert.assertEquals(true, hiveMetaService.deleteAll());
    }
}
