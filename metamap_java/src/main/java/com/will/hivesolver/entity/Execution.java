package com.will.hivesolver.entity;

import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

import javax.persistence.*;
import javax.persistence.Entity;
import java.util.Date;

/**
 * Created by root on 16-7-15.
 */
@Entity
@DynamicInsert
@DynamicUpdate
@Table(name = "executions")
public class Execution {
    @Id
    @GeneratedValue
    private Integer id;
    @Column(insertable = false, updatable = false)
    private Date startTime;
    private Date endTime;
    private Integer status;
    @Column(updatable = false)
    private String logLocation;
    private ETL etl;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Date getStartTime() {
        return startTime;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getEndTime() {
        return endTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getLogLocation() {
        return logLocation;
    }

    public void setLogLocation(String logLocation) {
        this.logLocation = logLocation;
    }

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "job_id")
    public ETL getEtl() {
        return etl;
    }

    public void setEtl(ETL etl) {
        this.etl = etl;
    }
}
