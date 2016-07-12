package com.will.hivesolver.service;

import com.will.hivesolver.dao.IMetaDao;
import com.will.hivesolver.entity.Meta;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

@Service("metaService")
public class MetaService {

    private static Logger log = LoggerFactory.getLogger(MetaService.class);
    
    @Resource(name = "metaDao")
    private IMetaDao metaDao;

    public void add(Meta meta) {
        if (meta.getId() > 0) {
            metaDao.update(meta);
        } else{
            meta.setValid(1);
            meta.setCtime(System.currentTimeMillis());
            metaDao.insert(meta);
        }
    }

    public Meta getById(int id) {
        return metaDao.getMetaById(id).get(0);
    }

    public List<Meta> getAll() {
        return metaDao.getAll();
    }
}
