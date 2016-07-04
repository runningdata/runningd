package com.will.hivesolver.util;

import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonUtil {

	private static ObjectMapper mapper;

	private static Logger log = LoggerFactory.getLogger(JsonUtil.class);

	public static ObjectMapper getMapperInstance(boolean createNew) {
		if (createNew) {
			mapper = new ObjectMapper();
			//mapper.setSerializationInclusion(Inclusion.NON_EMPTY);
			return mapper;
		} else if (mapper == null) {
			mapper = new ObjectMapper();
			//mapper.setSerializationInclusion(Inclusion.NON_EMPTY);
		}
		return mapper;
	}

	public static <T> T jToO(String json, Class<T> c) {
		T o = null;
		ObjectMapper mapper = getMapperInstance(false);
		try {
			o = mapper.readValue(json, c);
		} catch (IOException e) {
			log.error("json转化成对象时发生错误", e);
		}
		return o;
	}

	public static <T> String oToJ(T t) {
		ObjectMapper om = getMapperInstance(false);
		Writer w = new StringWriter();
		String json = null;
		try {
			om.writeValue(w, t);
			json = w.toString();
			w.close();
		} catch (IOException e) {
			log.error("对象转换成json时发生错误", e);
		}
		return json;
	}

	private static boolean isEmpty(Object obj) {
		boolean result = true;
		if (obj == null) {
			return true;
		}
		if (obj instanceof String) {
			result = (obj.toString().trim().length() == 0) || obj.toString().trim().equals("null");
		} else if (obj instanceof Collection<?>) {
			result = ((Collection<?>) obj).size() == 0;
		} else {
			result = ((obj == null) || (obj.toString().trim().length() < 1)) ? true : false;
		}
		return result;
	}

	/**
	 * 从json中读取tagPath处的值 tagPath用 :分隔
	 * 
	 * @param json
	 * @param tagPath
	 * @return
	 * @throws Exception
	 */
	public static <T> List<T> readValueFromJson(String json, String tagPath, Class<T> type) throws Exception {
		// 返回值
		List<T> value = new ArrayList<T>();
		if (isEmpty(json) || (isEmpty(tagPath))) {
			return value;
		}
		ObjectMapper mapper = getMapperInstance(false);
		String[] path = tagPath.split(":");
		JsonNode node = mapper.readTree(json);
		getJsonValue(node, path, value, 1, type);
		return value;
	}

	/**
	 * 序列化
	 *
	 * @throws Exception
	 */
	public static String writeValueAsString(Object o) throws Exception {
		return getMapperInstance(false).writeValueAsString(o);
	}

	private static <T> void getJsonValue(JsonNode node, String[] path, List<T> values, int nextIndex, Class<T> type) throws Exception {
		if (isEmpty(node)) {
			return;
		}
		// 是路径的最后就直接取值
		if (nextIndex == path.length) {
			if (node.isArray()) {
				for (int i = 0; i < node.size(); i++) {
					JsonNode child = node.get(i).get(path[nextIndex - 1]);
					if (isEmpty(child)) {
						continue;
					}
					values.add(getValue(child, type));
				}
			} else {
				JsonNode child = node.get(path[nextIndex - 1]);
				if (!isEmpty(child)) {
					values.add(getValue(child, type));
				}
			}
			return;
		}
		// 判断是Node下是集合还是一个节点
		node = node.get(path[nextIndex - 1]);
		if (node.isArray()) {
			for (int i = 0; i < node.size(); i++) {
				getJsonValue(node.get(i), path, values, nextIndex + 1, type);
			}
		} else {
			getJsonValue(node, path, values, nextIndex + 1, type);
		}
	}

	@SuppressWarnings("unchecked")
	private static <T> T getValue(JsonNode node, Class<T> type) throws Exception {
		String typeName = type.getSimpleName();
		if (typeName.equals("String"))
			typeName = "Text";
		else if (typeName.equals("Integer"))
			typeName = "Int";
		String methodName = "get" + typeName + "Value";
		Method method = node.getClass().getMethod(methodName);
		T t = (T) method.invoke(node);
		return t;
	}
	
	

}
