package com.will.hivesolver.util;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

@JsonInclude(Include.NON_EMPTY)
public class ResultBean<T> {
	/* 返回主体 */
	private T result;
	/* 操作是否成功 */
	private String status;
	/* 错误描述 */
	private String description;
	

	public T getResult() {
		return result;
	}

	public void setResult(T result) {
		this.result = result;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(ResultStatus status) {
		switch (status) {
		case SUCCESS:
			this.status = "SUCCESS";
			break;
		case FAIL:
			this.status = "FAIL";
			break;
		case ERROR:
			this.status = "ERROR";
			break;
		default:
			this.status = "ERROR";
			break;
		}
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public enum ResultStatus {
		SUCCESS, FAIL, ERROR
	}
}
