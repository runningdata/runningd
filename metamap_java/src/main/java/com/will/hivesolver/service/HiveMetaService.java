package com.will.hivesolver.service;

import java.util.List;

import javax.annotation.Resource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import com.will.hivesolver.dao.IColMetaDao;
import com.will.hivesolver.entity.ColMeta;

@Service("hiveMetaService")
public class HiveMetaService {

    private static Logger log = LoggerFactory.getLogger(HiveMetaService.class);

    @Resource(name = "iColMetaDao")
    private IColMetaDao iColMetaDao;

    @Resource(name = "hivemetaJdbcTemplate")
    private JdbcTemplate jdbcTemplate;

    public Object executeSql(String sql) {
        return jdbcTemplate.queryForList(sql);
    }
    public  List<ColMeta> selectColMeta() {
        return iColMetaDao.selectColMeta();
    }
    
    public  void insertColMeta() {
        iColMetaDao.insertColMeta();
    }
    
}
