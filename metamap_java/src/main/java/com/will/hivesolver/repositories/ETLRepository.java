package com.will.hivesolver.repositories;

import com.will.hivesolver.entity.ETL;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

/**
 * Created by will on 16-7-13.
 */
public interface ETLRepository extends JpaRepository<ETL, Integer>{
    List<ETL> findByValid(int valid);

    @Modifying
    @Query("update ETL set valid = 0 where tblName=:tblName")
    void makePreviousInvalid(@Param("tblName")String tblName);

    @Query("from ETL where tblName=:tableName and valid = 1")
    List<ETL> getETLByTblName(@Param("tableName")String tableName);

}
