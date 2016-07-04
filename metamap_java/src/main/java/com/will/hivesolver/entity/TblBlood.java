package com.will.hivesolver.entity;

public class TblBlood {
    private int id;
    private String tblName;
    private String parentTbl;
    private int relatedEtlId;
    private int valid = 1;
    private boolean isSelected;
    private long ctime;
    private long utime;
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
}
