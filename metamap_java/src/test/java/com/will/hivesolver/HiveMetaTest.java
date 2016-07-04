package com.will.hivesolver;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.commons.io.FileUtils;
import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.map.JsonMappingException;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import com.will.hivesolver.entity.ColMeta;
import com.will.hivesolver.entity.User;
import com.will.hivesolver.service.HiveMetaService;
import com.will.hivesolver.util.JsonUtil;
import com.will.hivesolver.util.ResultBean;

@RunWith(SpringJUnit4ClassRunner.class) 
@ContextConfiguration("/spring/applicationContext.xml") 
public class HiveMetaTest {
    private static Logger log = LoggerFactory.getLogger(HiveMetaTest.class);
    
//    @Resource(name="hiveMetaService")
    @Autowired
    private HiveMetaService hiveMetaService;
    
    @Test
    public void testResource() {
        
        System.out.println(HiveMetaTest.class.getResource("").getPath());
        System.out.println(this.getClass().getResource("/").getPath());
    }
    
    @Test
    public void testSql() {
        try {
            String sql = "";
            try {
                    sql = FileUtils.readFileToString(new File("/usr/local/odsdata_api/src/main/resources/all.sql"));;
            } catch (IOException e) {
                log.error("error hadppens : " + e.getMessage());
            }
            System.out.println("sql is " + sql);
            ResultBean<User> resultBean = new ResultBean<User>();

            System.out.println(JsonUtil.getMapperInstance(false).writeValueAsString(hiveMetaService.executeSql(sql)));
        } catch (JsonGenerationException e) {
            e.printStackTrace();
        } catch (JsonMappingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    @Test
    public void testSelectColMeta() {
        List<ColMeta> testyinkerDao = hiveMetaService.selectColMeta();
        for (ColMeta meta : testyinkerDao) {
            System.out.println(meta);
        }
    }
    
    @Test
    public void testDB() throws JsonGenerationException, JsonMappingException, IOException {
        System.out.println(JsonUtil.getMapperInstance(false).writeValueAsString(hiveMetaService.executeSql("show tables")));
    }
    
    @Test
    public void testinsertColMeta() {
        hiveMetaService.insertColMeta();
    }
    
}
