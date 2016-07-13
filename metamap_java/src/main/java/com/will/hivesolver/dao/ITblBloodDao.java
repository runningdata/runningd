package com.will.hivesolver.dao;

import java.util.List;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import org.springframework.stereotype.Repository;

import com.will.hivesolver.entity.TblBlood;

@Repository("tblBloodDao")
public interface ITblBloodDao {
    @Select("select * from tbl_blood where valid = 1")
    public List<TblBlood> selectAll();
    
    @Select("select * from tbl_blood where valid = 1 and tbl_name=#{tblName}")
    public List<TblBlood> selectByTblName(@Param("tblName")String tblName);

    @Select("select * from tbl_blood where related_etl_id=#{id}")
    public List<TblBlood> selectByETLId(@Param("id")int id);

    @Select("select b.* from"
            + " tbl_blood a join tbl_blood b"
            + " on a.parent_tbl = b.tbl_name and b.valid = 1"
            + " where a.valid = 1 and a.tbl_name = #{tblName}")
    public List<TblBlood> selectParentByTblName(@Param("tblName")String tblName);
    
    @Select("select a.* from "
            + "(select * from tbl_blood where valid = 1) a"
            + " left outer join "
            + "(select distinct parent_tbl from tbl_blood where valid = 1) b"
            + " on a.tbl_name = b.parent_tbl"
            + " where b.parent_tbl is null")
    public List<TblBlood> selectAllLeaf();
    
    @Select("select * from tbl_blood where valid = 1 and parent_tbl=#{tblName}")
    public List<TblBlood> selectByParentTblName(@Param("tblName")String tblName);

}
