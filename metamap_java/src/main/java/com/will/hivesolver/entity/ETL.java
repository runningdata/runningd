package com.will.hivesolver.entity;
/**
 * 
 * @author will
 *
 */
public class ETL {
    private int id;
    private String query;
    private String meta;
    private String tblName;
    private String author;
    private String preSql;
    private int priority;
    private int onSchedule;
    private int valid = 1;
    private long ctime;
    private long utime;
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    
    public String getQuery() {
        return query;
    }
    public void setQuery(String query) {
        this.query = query;
    }
    public String getMeta() {
        return meta;
    }
    public void setMeta(String meta) {
        this.meta = meta;
    }
    public String getTblName() {
        return tblName;
    }
    public void setTblName(String tblName) {
        this.tblName = tblName;
    }
    public String getAuthor() {
        return author;
    }
    public void setAuthor(String author) {
        this.author = author;
    }
    public String getPreSql() {
        return preSql;
    }
    public void setPreSql(String preSql) {
        this.preSql = preSql;
    }
    public int getOnSchedule() {
        return onSchedule;
    }
    public void setOnSchedule(int onSchedule) {
        this.onSchedule = onSchedule;
    }
    public int getValid() {
        return valid;
    }
    public void setValid(int valid) {
        this.valid = valid;
    }
    public long getCtime() {
        return ctime;
    }
    public void setCtime(long ctime) {
        this.ctime = ctime;
    }
    public long getUtime() {
        return utime;
    }
    public void setUtime(long utime) {
        this.utime = utime;
    }
    public int getPriority() {
        return priority;
    }
    public void setPriority(int priority) {
        this.priority = priority;
    }
}
