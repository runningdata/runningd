package com.will.hivesolver.util;

import java.util.Map;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.NameValuePair;
import org.apache.commons.httpclient.methods.PostMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HttpClientUtil {

	private static Logger log = LoggerFactory.getLogger(HttpClientUtil.class);

	private HttpClient httpClient;

	public String sendPost(String url, Map<String, String> params) {
		String result = null;
		PostMethod post = new PostMethod(url);
		for (String key : params.keySet()) {
			post.addParameter(new NameValuePair(key, params.get(key)));
		}
		try {
			int status = httpClient.executeMethod(post);
			if (status == HttpStatus.SC_OK) {
				result = post.getResponseBodyAsString().trim();
			}
		} catch (Exception e) {
			log.error("获取远程数据失败：" + url, e);
		} finally {
			post.releaseConnection();
		}
		return result;
	}

	public String sendPost(String url) {
		String result = null;
		PostMethod post = new PostMethod(url);
		try {
			int status = httpClient.executeMethod(post);
			if (status == HttpStatus.SC_OK) {
				result = post.getResponseBodyAsString().trim();
			}
		} catch (Exception e) {
			log.error("获取远程数据失败：" + url, e);
		} finally {
			post.releaseConnection();
		}
		return result;
	}

	public HttpClient getHttpClient() {
		return httpClient;
	}

	public void setHttpClient(HttpClient httpClient) {
		this.httpClient = httpClient;
	}

}
