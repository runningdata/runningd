package com.will.hivesolver.entity;

import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

import javax.persistence.*;
import java.util.Date;

/**
 * Created by will on 16-7-11.
 */
@javax.persistence.Entity
@DynamicUpdate
@DynamicInsert
@Table(name = "metas")
public class Meta {
    public static final int TYPE_MYSQL = 1;
    public static final int TYPE_HIVE = 2;

    @Id
    @GeneratedValue
    private int id;
    private String meta;
    private String db;
    private String settings;
    private int type; // 1. mysql 2. hive
    private int valid;
    @Column(updatable = false, insertable = false)
    private Date ctime;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getMeta() {
        return meta;
    }

    public void setMeta(String meta) {
        this.meta = meta;
    }

    public String getDb() {
        return db;
    }

    public void setDb(String db) {
        this.db = db;
    }

    public int getValid() {
        return valid;
    }

    public void setValid(int valid) {
        this.valid = valid;
    }


    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    public String getSettings() {
        return settings;
    }

    public void setSettings(String settings) {
        this.settings = settings;
    }
}
