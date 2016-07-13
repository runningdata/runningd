package com.will.hivesolver.entity;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;

import org.apache.commons.lang.builder.EqualsBuilder;
import org.apache.commons.lang.builder.HashCodeBuilder;
import org.apache.commons.lang.builder.ReflectionToStringBuilder;
import org.apache.commons.lang.builder.ToStringStyle;
import org.apache.commons.lang.reflect.MethodUtils;

@SuppressWarnings("serial")
public abstract class Entity implements Serializable {
	
	@Override
	public String toString() {
		return ReflectionToStringBuilder.reflectionToString(this);
	}

	public String toSimpleString() {
		return ReflectionToStringBuilder.reflectionToString(this, ToStringStyle.SIMPLE_STYLE);
	}

	@Override
	public boolean equals(Object o) {
		return EqualsBuilder.reflectionEquals(this, o);
	}

	@Override
	public int hashCode() {
		return HashCodeBuilder.reflectionHashCode(this);
	}
	
	@SuppressWarnings("unchecked")
	public <T> T invokeMethod(String methodName, Object[] args) throws NoSuchMethodException, IllegalAccessException, InvocationTargetException {
		return (T) MethodUtils.invokeMethod(this, methodName, args);
	}
}