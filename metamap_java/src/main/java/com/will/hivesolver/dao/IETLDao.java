package com.will.hivesolver.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import org.springframework.stereotype.Repository;

import com.will.hivesolver.entity.ETL;

@Repository("etlDao")
public interface IETLDao {

    @Select("select * from etl where tbl_name=#{tableName} and valid = 1")
    public List<ETL> getETLByTblName(@Param("tableName")String tableName);

    @Select("select * from etl where id = #{id}")
    public List<ETL> getETLById(@Param("id") int id);

    @Select("select parent_tbl from etl where tbl_name=#{tableName} and valid = 1")
    public List<String> getParentTblName(@Param("tableName")String tableName);

    
    @Select("SELECT * FROM etl where valid = 1")
    public List<ETL> selectAllValidETL();
    

}
