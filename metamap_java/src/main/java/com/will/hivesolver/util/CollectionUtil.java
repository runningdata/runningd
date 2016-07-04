package com.will.hivesolver.util;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class CollectionUtil {

	public static List<Map<String, Object>> assembleResult(@SuppressWarnings("unchecked") List<Map<String, Object>>... lists) {
		Set<String> dateSet = new HashSet<>();
		List<Map<String, Object>> assembleList = new ArrayList<>();
		for (List<Map<String, Object>> resultList : lists) {
			for (Map<String, Object> result : resultList) {
				for (Map.Entry<String, Object> entry : result.entrySet()) {
					if (entry.getKey().equals("date"))
						dateSet.add(String.valueOf(entry.getValue()));
				}
			}
		}
		for (String date : dateSet) {
			Map<String, Object> assemble = new HashMap<>();
			for (List<Map<String, Object>> resultList : lists) {
				for (Map<String, Object> result : resultList) {
					String d = String.valueOf(result.get("date"));
					if (d.equals(date))
						assemble.putAll(result);
				}
			}
			assembleList.add(assemble);
		}
		Collections.sort(assembleList, new Comparator<Map<String, Object>>() {

			@Override
			public int compare(Map<String, Object> o1, Map<String, Object> o2) {
				String date1 = String.valueOf(o1.get("date"));
				String date2 = String.valueOf(o2.get("date"));
				return date2.compareTo(date1);
			}

		});
		return assembleList;
	}

	public static List<Map<String, Object>> assembleResult(final String link, @SuppressWarnings("unchecked") List<Map<String, Object>>... lists) {
		Set<String> keySet = new HashSet<>();
		List<Map<String, Object>> assembleList = new ArrayList<>();
		for (List<Map<String, Object>> resultList : lists) {
			for (Map<String, Object> result : resultList) {
				for (Map.Entry<String, Object> entry : result.entrySet()) {
					if (entry.getKey().equals(link))
						keySet.add(String.valueOf(entry.getValue()));
				}
			}
		}
		for (String key : keySet) {
			Map<String, Object> assemble = new HashMap<>();
			for (List<Map<String, Object>> resultList : lists) {
				for (Map<String, Object> result : resultList) {
					String l = String.valueOf(result.get(link));
					if (l.equals(key))
						assemble.putAll(result);
				}
			}
			assembleList.add(assemble);
		}
		Collections.sort(assembleList, new Comparator<Map<String, Object>>() {

			@Override
			public int compare(Map<String, Object> o1, Map<String, Object> o2) {
				String date1 = String.valueOf(o1.get(link));
				String date2 = String.valueOf(o2.get(link));
				return date2.compareTo(date1);
			}

		});
		return assembleList;
	}
}
