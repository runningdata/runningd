package com.will.hivesolver.entity;

public class ColMeta {
    private int dbId;
    private String dbName;
    private int tblId;
    private String tblType;
    private String colTypeName;
    private String colComment;
    private String colName;
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
    @Override
    public String toString() {
        return "ColMeta [dbId=" + dbId + ", dbName=" + dbName + ", tblId="
                + tblId + ", tblType=" + tblType + ", colTypeName="
                + colTypeName + ", colComment=" + colComment + ", colName="
                + colName + "]";
    }
    
}
