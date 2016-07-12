package com.will.hivesolver.dao;

import com.will.hivesolver.entity.Meta;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository("metaDao")
public interface IMetaDao {
    @Select("insert into metas  "
            + "(meta, db, settings, valid, ctime,type)   values "
            + "  (#{meta}, #{db}, #{settings}, #{valid}, #{ctime},#{type}) ")
    public void insert(Meta meta);

    @Update("update metas set meta=#{meta}, db=#{db}, settings=#{settings}, valid=#{valid}, type=#{type}" +
            " where id = #{id}")
    public void update(Meta meta);
    
    @Select("select * from metas where meta=#{meta} and valid = 1")
    public List<Meta> getByName(@Param("meta") String meta);

    @Select("select * from metas where id = #{id}")
    public List<Meta> getMetaById(@Param("id") int id);


    @Select("SELECT * FROM metas where valid = 1")
    public List<Meta> getAll();
    
}
