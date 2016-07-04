package com.will.hivesolver.dao;

import java.util.List;

import org.springframework.stereotype.Repository;

import com.will.hivesolver.entity.ColMeta;

@Repository("iColMetaDao")
public interface IColMetaDao {
    public List<ColMeta> selectColMeta();

    public void insertColMeta();

}
