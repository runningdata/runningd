package com.will.hivesolver.repositories;

import com.will.hivesolver.entity.ColMeta;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/**
 * Created by will on 16-7-13.
 */
public interface ColMetaRepository extends JpaRepository<ColMeta, Integer>{
    public List<ColMeta> findByColName(String colName);
}
