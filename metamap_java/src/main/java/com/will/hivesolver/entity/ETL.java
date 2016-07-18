package com.will.hivesolver.entity;

import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

import javax.persistence.Column;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.Table;
import java.util.Date;

/**
 * 
 * @author will
 *
 */
@javax.persistence.Entity
@DynamicUpdate
@DynamicInsert
@Table(name = "etl")
public class ETL {
    @Id
    @GeneratedValue
    private int id;
    private String query;
    private String meta;
    private String tblName;
    private String author;
    private String preSql;
    private int priority;
    private int onSchedule;
    private int valid = 1;
    @Column(updatable = false, insertable = false)
    private Date ctime;
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
    public int getPriority() {
        return priority;
    }
    public void setPriority(int priority) {
        this.priority = priority;
    }

    public Date getCtime() {
        return ctime;
    }

    public void setCtime(Date ctime) {
        this.ctime = ctime;
    }
}
