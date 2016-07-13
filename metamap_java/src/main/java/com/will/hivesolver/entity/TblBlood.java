package com.will.hivesolver.entity;

import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

import javax.persistence.*;
import java.util.Date;

@javax.persistence.Entity
@DynamicUpdate
@DynamicInsert
@Table(name = "tbl_blood")
public class TblBlood {
    @Id
    @GeneratedValue
    private int id;
    private String tblName;
    private String parentTbl;
    private int relatedEtlId;
    private int valid = 1;
    @Transient
    private boolean isSelected;


    @Column(updatable = false, insertable = false)
    private Date ctime;

    @Column(updatable = true, insertable = false)
    private Date utime;
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    public String getTblName() {
        return tblName;
    }
    public void setTblName(String tblName) {
        this.tblName = tblName;
    }
    public String getParentTbl() {
        return parentTbl;
    }
    public void setParentTbl(String parentTbl) {
        this.parentTbl = parentTbl;
    }
    public int getRelatedEtlId() {
        return relatedEtlId;
    }
    public void setRelatedEtlId(int relatedEtlId) {
        this.relatedEtlId = relatedEtlId;
    }
    public int getValid() {
        return valid;
    }
    public void setValid(int valid) {
        this.valid = valid;
    }
    public boolean isSelected() {
        return isSelected;
    }
    public void setSelected(boolean isSelected) {
        this.isSelected = isSelected;
    }

    public Date getCtime() {
        return ctime;
    }

    public void setCtime(Date ctime) {
        this.ctime = ctime;
    }

    public Date getUtime() {
        return utime;
    }

    public void setUtime(Date utime) {
        this.utime = utime;
    }
}
