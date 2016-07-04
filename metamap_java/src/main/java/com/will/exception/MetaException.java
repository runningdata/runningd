package com.will.exception;

public class MetaException extends RuntimeException {

	/**
	 * serialVersionUID
	 * <p>
	 * 变量描述
	 * </p>
	 */

	private static final long serialVersionUID = 1L;

	private String code;
	private String message;

	public MetaException(String message) {
		super();
		this.message = message;

	}

	public MetaException(String code, String message) {
		super();
		this.code = code;
		this.message = message;
	}

	public String getCode() {
		return code;
	}

	public void setCode(String code) {
		this.code = code;
	}

	public String getMessage() {
		return message;
	}

	public void setMessage(String message) {
		this.message = message;
	}

}
