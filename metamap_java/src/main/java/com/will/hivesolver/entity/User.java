package com.will.hivesolver.entity;

import java.math.BigDecimal;

import org.apache.ibatis.type.Alias;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

@JsonInclude(Include.NON_EMPTY)
@Alias("User")
public class User extends Entity {

	/**
	 * serialVersionUID
	 * <p>
	 * 变量描述
	 * </p>
	 */

	private static final long serialVersionUID = 1555454004663409085L;
	private Long userId;
	private String nickName;
	private String realName;
	private String idCardNo;
	private String email;
	private String openTime;
	private BigDecimal investAmount1st;
	private String rfmLevel;
	private String source;

	public String getNickName() {
		return nickName;
	}

	public String getRfmLevel() {
		return rfmLevel;
	}

	public void setRfmLevel(String rfmLevel) {
		this.rfmLevel = rfmLevel;
	}

	public String getSource() {
		return source;
	}

	public void setSource(String source) {
		this.source = source;
	}

	public void setNickName(String nickName) {
		this.nickName = nickName;
	}

	public String getRealName() {
		return realName;
	}

	public void setRealName(String realName) {
		this.realName = realName;
	}

	public String getIdCardNo() {
		return idCardNo;
	}

	public void setIdCardNo(String idCardNo) {
		this.idCardNo = idCardNo;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getOpenTime() {
		return openTime;
	}

	public void setOpenTime(String openTime) {
		this.openTime = openTime;
	}

	public BigDecimal getInvestAmount1st() {
		return investAmount1st;
	}

	public void setInvestAmount1st(BigDecimal investAmount1st) {
		this.investAmount1st = investAmount1st;
	}

	public Long getUserId() {
		return userId;
	}

	public void setUserId(Long userId) {
		this.userId = userId;
	}

}
