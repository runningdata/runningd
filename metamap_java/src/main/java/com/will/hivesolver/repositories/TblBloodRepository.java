package com.will.hivesolver.repositories;

import com.will.hivesolver.entity.TblBlood;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
/**
 * Created by will on 16-7-13.
 */
public interface TblBloodRepository extends JpaRepository<TblBlood, Integer>{
    List<TblBlood> findByValid(int valid);
    TblBlood findByTblName(String tblName);

//    @Query("select a from "
//            + "(from TblBlood where valid = 1) a"
//            + " left outer join "
//            + "(select distinct parentTbl from TblBlood where valid = 1) b"
//            + " on a.tblName = b.parentTbl"
//            + " where b.parentTbl is null")
//    List<TblBlood> selectAllLeaf();

    @Modifying
    @Query("update TblBlood set valid = 0 where tblName=:tblName")
    void makePreviousInvalid(@Param("tblName")String tblName);

//    @Query("select b from"
//            + " TblBlood a join TblBlood b"
//            + " on a.parentTbl = b.tblName and b.valid = 1"
//            + " where a.valid = 1 and a.tblName = ?1")
//    List<TblBlood> selectParentByTblName(String tblName);

    @Query("from TblBlood where valid = 1 and parentTbl=:tblName")
    public List<TblBlood> selectByParentTblName(@Param("tblName")String tblName);

    @Query("from TblBlood where valid = 1 and tblName=:tblName")
    List<TblBlood> selectByTblName(@Param("tblName")String tblName);
}
