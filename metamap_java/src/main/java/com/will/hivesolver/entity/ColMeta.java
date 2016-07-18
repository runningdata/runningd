package com.will.hivesolver.entity;

import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

import javax.persistence.Column;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.Table;
import java.util.Date;

@javax.persistence.Entity
@DynamicUpdate
@DynamicInsert
@Table(name = "col_tbl_db")
public class ColMeta {
    @Id
    @GeneratedValue
    private int id;
    private int dbId;
    private String dbName;
    private int tblId;
    private String tblType;
    private String tblName;
    private String colTypeName;
    private String colComment;
    private String colName;
    @Column(updatable = false, insertable = false)
    private Date ctime;

    public int getDbId() {
        return dbId;
    }
    public void setDbId(int dbId) {
        this.dbId = dbId;
    }
    public String getDbName() {
        return dbName;
    }
    public void setDbName(String dbName) {
        this.dbName = dbName;
    }
    public int getTblId() {
        return tblId;
    }
    public void setTblId(int tblId) {
        this.tblId = tblId;
    }
    public String getTblType() {
        return tblType;
    }
    public void setTblType(String tblType) {
        this.tblType = tblType;
    }
    public String getColTypeName() {
        return colTypeName;
    }
    public void setColTypeName(String colTypeName) {
        this.colTypeName = colTypeName;
    }
    public String getColComment() {
        return colComment;
    }
    public void setColComment(String colComment) {
        this.colComment = colComment;
    }
    public String getColName() {
        return colName;
    }
    public void setColName(String colName) {
        this.colName = colName;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public Date getCtime() {
        return ctime;
    }

    public void setCtime(Date ctime) {
        this.ctime = ctime;
    }

    public String getTblName() {
        return tblName;
    }

    public void setTblName(String tblName) {
        this.tblName = tblName;
    }
}
