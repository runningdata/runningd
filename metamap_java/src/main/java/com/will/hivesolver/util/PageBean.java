package com.will.hivesolver.util;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

@JsonInclude(Include.NON_EMPTY)
public class PageBean<T> {

	private int pageIndex = 1; // 需要显示的页码
	private int totalPages; // 总页数
	private int pageSize = 20; // 每页记录数
	private int totalRecords = 0; // 总记录数
	private boolean isHavePrePage = false; // 是否有上一页
	private boolean isHaveNextPage = false; // 是否有下一页

	private List<T> dataList = new ArrayList<T>();

	public void setPageBean(int totalRecords, int pageIndex, int pageSize, List<T> dataList) {
		this.pageIndex = pageIndex;
		this.pageSize = pageSize;

		if (totalRecords < 0) {
			throw new RuntimeException("总记录数不能小于0!");
		}
		// 设置总记录数
		this.totalRecords = totalRecords;
		// 计算总页数
		this.totalPages = this.totalRecords / this.pageSize;
		if (this.totalRecords % this.pageSize != 0) {
			this.totalPages++;
		}
		
		// 计算是否有上一页
		if (this.pageIndex > 1) {
			this.isHavePrePage = true;
		} else {
			this.isHavePrePage = false;
			this.pageIndex = 1;
		}
		// 计算是否有下一页
		if (this.pageIndex < this.totalPages) {
			this.isHaveNextPage = true;
		} else {
			this.isHaveNextPage = false;
			this.pageIndex = this.totalPages;
		}

		this.dataList = dataList;
	}

	public int getPageIndex() {
		return pageIndex;
	}

	public int getPageSize() {
		return pageSize;
	}

	public int getTotalRecords() {
		return totalRecords;
	}

	public int getTotalPages() {
		return totalPages;
	}

	public boolean isHavePrePage() {
		return isHavePrePage;
	}

	public boolean isHaveNextPage() {
		return isHaveNextPage;
	}

	public List<T> getDataList() {
		return dataList;
	}

}
