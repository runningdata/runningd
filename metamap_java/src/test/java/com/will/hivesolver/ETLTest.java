package com.will.hivesolver;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import com.will.hivesolver.entity.*;
import com.will.hivesolver.util.JsonUtil;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.hadoop.hive.metastore.api.MetaException;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import com.will.hivesolver.service.ETLService;
import com.will.hivesolver.service.TblBloodService;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/spring/applicationContext.xml")
public class ETLTest {
    private static Logger log = LoggerFactory.getLogger(ETLTest.class);

    @Autowired
    private ETLService etlService;

    @Autowired
    private TblBloodService tblBloodService;

    @Test
    public void testinsertEtl() {
        ETL etl = new ETL();
        etl.setAuthor("will");
        etl.setCtime(System.currentTimeMillis() / 1000);
        etl.setUtime(System.currentTimeMillis() / 1000);
        etl.setMeta("mymeta");
        etl.setTblName("my_table");
        etl.setPreSql("delete from default.tbl");
        etl.setQuery("select * from batting");
        etl.setValid(1);
        etl.setOnSchedule(1);
        etlService.addETL(etl);
    }

    @Test
    public void testCompar() {
        Map<String, Node> map = new HashMap();
        Node node1 = new Node();
        node1.setLevel(1);
        node1.setName("1");
        map.put(node1.getName(), node1);
        Node node3 = new Node();
        node3.setLevel(2);
        node3.setName("3");
        map.put(node3.getName(), node3);
        Node node2 = new Node();
        node2.setLevel(2);
        node2.setName("2");
        map.put(node2.getName(), node2);
        Set<Node> nodes = new TreeSet<Node>();
        nodes.addAll(map.values());
        Iterator<Node> iterator = nodes.iterator();
        Node root = new Node();
        int currentLevel = 1000;
        Node currentParent = null;
        while (iterator.hasNext()) {
            Node node = iterator.next();
            System.out.println("nnn: " + node.getName());
            
        }
    }

    @Test
    public void testTblBlood() {
        tblBloodService.resolveDependency();
    }
    
    @Test
    public void testGetTree() {
        etlService.getETLTree("mymeta@my_table");
    }

    @Test
    public void testGetMermaid() {
        for (TblBlood blood : etlService.getETLMermaid("mymeta@my_table")) {
            System.out.println(blood.getTblName());
        }
    }
    
    @Test
    public void testGenerateAzkabanTree() throws MetaException, ArchiveException {
        etlService.generateAzkabanDAG();
    }

    @Test
    public void testAllETL() throws Exception {
        System.out.println(JsonUtil.writeValueAsString(etlService.allETL()));
        ;
    }

    @Test
    public void testETLShell() throws Exception {
        System.out.println(JsonUtil.writeValueAsString(etlService.generateETLScript(1)));
    }

}
