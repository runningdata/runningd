package com.will.hivesolver;

import com.will.hivesolver.entity.Meta;
import com.will.hivesolver.service.MetaService;
import com.will.hivesolver.util.JsonUtil;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import java.util.List;

/**
 * Created by will on 16-7-11.
 */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/applicationContext.xml")
public class MetasTest {
    @Autowired
    private MetaService metaService;

    @Test
    public void testinsert() {
        Meta meta = new Meta();
        meta.setMeta("hive");
        meta.setDb("default");
        meta.setType(Meta.TYPE_HIVE);
        meta.setValid(1);
        metaService.save(meta);
    }

    @Test
    public void testUpdate() {
        Meta meta = new Meta();
        meta.setId(1);
        meta.setMeta("hive");
        meta.setDb("default");
        meta.setType(Meta.TYPE_HIVE);
        meta.setValid(1);
        metaService.save(meta);
    }

    @Test
    public void testGetAll() throws Exception {
        List<Meta> all = metaService.getAll();
        System.out.println("All ............");
        System.out.println(JsonUtil.writeValueAsString(all));
    }


    @Test
    public void testGetONe() throws Exception  {
        System.out.println("testGetONe ............");
        System.out.println(JsonUtil.writeValueAsString(metaService.getById(1)));
    }

    @Test
    public void testDeleteForeverONe() throws Exception  {
        System.out.println("testDeleteForeverONe ............");
        System.out.println(JsonUtil.writeValueAsString(metaService.deleteForever(2)));
        System.out.println(JsonUtil.writeValueAsString(metaService.getAll()));
    }
}
