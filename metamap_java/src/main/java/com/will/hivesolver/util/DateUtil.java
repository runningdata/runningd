package com.will.hivesolver.util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DateUtil {
	protected static Logger log = LoggerFactory.getLogger(DateUtil.class);

	private static String datePattern = "yyyy-MM-dd";

	private static String timePattern = "HH:mm";

	private static String datetimePattern = datePattern + " " + timePattern;

	public static String getTodayDateTime() {
	    SimpleDateFormat format = new SimpleDateFormat("yyyMMddHHmmss");
	    return format.format(new Date());
	}
	
	/**
	 * Return 缺省的日期格式 (yyyy-MM-dd)
	 * 
	 * @return 在页面中显示的日期格式
	 */
	public static String getDatePattern() {
		return datePattern;
	}

	/**
	 * 根据日期格式，返回日期按datePattern格式转换后的字符串
	 * 
	 * @param aDate
	 *            日期对象
	 * @return 格式化后的日期的页面显示字符串
	 */
	public static final String getDate(Date aDate) {
		SimpleDateFormat df = null;
		String returnValue = "";

		if (aDate != null) {
			df = new SimpleDateFormat(datePattern);
			returnValue = df.format(aDate);
		}

		return (returnValue);
	}

	/**
	 * 按照日期格式，将字符串解析为日期对象
	 * 
	 * @param aMask
	 *            输入字符串的格式
	 * @param strDate
	 *            一个按aMask格式排列的日期的字符串描述
	 * @return Date 对象
	 * @see java.text.SimpleDateFormat
	 * @throws ParseException
	 */
	public static final Date convertStringToDate(String aMask, String strDate) throws ParseException {
		SimpleDateFormat df = null;
		Date date = null;
		df = new SimpleDateFormat(aMask);

		if (log.isDebugEnabled()) {
			log.debug("converting '" + strDate + "' to date with mask '" + aMask + "'");
		}

		try {
			date = df.parse(strDate);
		} catch (ParseException pe) {
			// log.error("ParseException: " + pe);
			throw new ParseException(pe.getMessage(), pe.getErrorOffset());
		}

		return (date);
	}

	/**
	 * This method returns the current date time in the format: yyyy-MM-dd HH:MM
	 * a
	 * 
	 * @param theTime
	 *            the current time
	 * @return the current date/time
	 */
	public static String getTimeNow(Date theTime) {
		return getDateTime(timePattern, theTime);
	}

	/**
	 * This method returns the current date in the format: yyyy-MM-dd
	 * 
	 * @return the current date
	 * @throws ParseException
	 */
	public static Calendar getToday() throws ParseException {
		Date today = new Date();
		SimpleDateFormat df = new SimpleDateFormat(datePattern);

		// This seems like quite a hack (date -> string -> date),
		// but it works ;-)
		String todayAsString = df.format(today);
		Calendar cal = new GregorianCalendar();
		cal.setTime(convertStringToDate(todayAsString));

		return cal;
	}

	/**
	 * This method generates a string representation of a date's date/time in
	 * the format you specify on input
	 * 
	 * @param aMask
	 *            参数模板为用户自定义模板例如:yyyy-MM-dd HH:mm:SS
	 * @param aDate
	 *            日期对象
	 * @return 返回一个根据模板将日期类型转换的字符串
	 * 
	 * @see java.text.SimpleDateFormat
	 */
	public static final String getDateTime(String aMask, Date aDate) {
		SimpleDateFormat df = null;
		String returnValue = "";

		if (aDate == null) {
			log.error("aDate is null!");
		} else {
			df = new SimpleDateFormat(aMask);
			returnValue = df.format(aDate);
		}

		return (returnValue);
	}

	/***************************************************************************
	 * 将日期对象转换成代年日月时分的字符串格式
	 * 
	 * @param aDate日期类型
	 * @return 返回类型为String 格式为yyyy-MM-dd HH:mm
	 */
	public static final String getDateTime(Date aDate) {
		SimpleDateFormat df = new SimpleDateFormat(datetimePattern);
		String returnValue = "";

		if (aDate == null) {
			log.error("aDate is null!");
		} else {
			returnValue = df.format(aDate);
		}
		return (returnValue);
	}

	/**
	 * 根据日期格式，返回日期按datePattern格式转换后的字符串
	 * 
	 * @param aDate
	 * @return
	 */
	public static final String convertDateToString(Date aDate) {
		return getDateTime(datePattern, aDate);
	}

	public static final String convertDateToString(Date aDate, String pattern) {
		return getDateTime(pattern, aDate);
	}

	/**
	 * 按照日期格式，将字符串解析为日期对象
	 * 
	 * @param strDate
	 *            (格式 yyyy-MM-dd)
	 * @return
	 * 
	 * @throws ParseException
	 */
	public static Date convertStringToDate(String strDate) throws ParseException {
		Date aDate = null;

		try {
			if (log.isDebugEnabled()) {
				log.debug("converting date with pattern: " + datePattern);
			}

			aDate = convertStringToDate(datePattern, strDate);
		} catch (ParseException pe) {
			log.error("Could not convert '" + strDate + "' to a date, throwing exception");
			pe.printStackTrace();
			throw new ParseException(pe.getMessage(), pe.getErrorOffset());

		}

		return aDate;
	}

	// ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝庄开智添加＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝//
	/**
	 * 按照日期格式，将字符串解析为日期对象
	 * 
	 * @param strDate
	 *            (格式 yyyy-MM-dd HH:mm)
	 * @return
	 * @throws ParseException
	 * 
	 * @throws ParseException
	 */
	public static Date convertStringToDateTime(String strDate) throws ParseException {
		Date aDate = null;

		try {
			if (log.isDebugEnabled()) {
				log.debug("converting date with pattern: " + datetimePattern);
			}

			aDate = convertStringToDate(datetimePattern, strDate);
		} catch (ParseException pe) {
			log.error("Could not convert '" + strDate + "' to a date, throwing exception");
			pe.printStackTrace();
			throw new ParseException(pe.getMessage(), pe.getErrorOffset());

		}

		return aDate;
	}

	/**
	 * 判断指定日期的年份是否是闰年
	 */
	public static boolean isLeapYear() {
		Calendar cal = Calendar.getInstance();
		int year = cal.get(Calendar.YEAR);
		return isLeapYear(year);
	}

	public static boolean isLeapYear(int year) {
		/**
		 * 详细设计： 1.被400整除是闰年，否则： 2.不能被4整除则不是闰年 3.能被4整除同时不能被100整除则是闰年
		 * 3.能被4整除同时能被100整除则不是闰年
		 */
		if ((year % 400) == 0)
			return true;
		else if ((year % 4) == 0) {
			if ((year % 100) == 0)
				return false;
			else
				return true;
		} else
			return false;
	}

	/**
	 * 判断指定日期的年份是否是闰年
	 * 
	 * @param date指定日期
	 *            。
	 * @return 是否闰年
	 */
	public static boolean isLeapYear(Date date) {
		/**
		 * 详细设计： 1.被400整除是闰年，否则： 2.不能被4整除则不是闰年 3.能被4整除同时不能被100整除则是闰年
		 * 3.能被4整除同时能被100整除则不是闰年
		 */

		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		int year = gc.get(Calendar.YEAR);
		return isLeapYear(year);
	}

	public static boolean isLeapYear(Calendar gc) {
		/**
		 * 详细设计： 1.被400整除是闰年，否则： 2.不能被4整除则不是闰年 3.能被4整除同时不能被100整除则是闰年
		 * 3.能被4整除同时能被100整除则不是闰年
		 */
		int year = gc.get(Calendar.YEAR);
		return isLeapYear(year);
	}

	// －－－－－－－－－－－－－－－－－－－与星期有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//
	/**
	 * 取得指定日期的所处星期的第一天
	 * 
	 * @param date指定日期
	 *            。
	 * @return 指定日期的所处星期的第一天
	 */
	public static Date getFirstDayOfWeek(Date date) {
		/**
		 * 详细设计： 1.如果date是星期日，则减0天 2.如果date是星期一，则减1天 3.如果date是星期二，则减2天
		 * 4.如果date是星期三，则减3天 5.如果date是星期四，则减4天 6.如果date是星期五，则减5天
		 * 7.如果date是星期六，则减6天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		switch (gc.get(Calendar.DAY_OF_WEEK)) {
		case (Calendar.SUNDAY):
			gc.add(Calendar.DATE, 0);
			break;
		case (Calendar.MONDAY):
			gc.add(Calendar.DATE, -1);
			break;
		case (Calendar.TUESDAY):
			gc.add(Calendar.DATE, -2);
			break;
		case (Calendar.WEDNESDAY):
			gc.add(Calendar.DATE, -3);
			break;
		case (Calendar.THURSDAY):
			gc.add(Calendar.DATE, -4);
			break;
		case (Calendar.FRIDAY):
			gc.add(Calendar.DATE, -5);
			break;
		case (Calendar.SATURDAY):
			gc.add(Calendar.DATE, -6);
			break;
		}
		return gc.getTime();
	}

	/**
	 * 取得指定日期的所处星期的第一天
	 * 
	 * @param gc参数为Calendar类型
	 * @return 指定日期的所处星期的第一天
	 */
	public static Calendar getFirstDayOfWeek(Calendar gc) {
		/**
		 * 详细设计： 1.如果date是星期日，则减0天 2.如果date是星期一，则减1天 3.如果date是星期二，则减2天
		 * 4.如果date是星期三，则减3天 5.如果date是星期四，则减4天 6.如果date是星期五，则减5天
		 * 7.如果date是星期六，则减6天
		 */
		switch (gc.get(Calendar.DAY_OF_WEEK)) {
		case (Calendar.SUNDAY):
			gc.add(Calendar.DATE, 1);
			break;
		case (Calendar.MONDAY):
			gc.add(Calendar.DATE, 0);
			break;
		case (Calendar.TUESDAY):
			gc.add(Calendar.DATE, -1);
			break;
		case (Calendar.WEDNESDAY):
			gc.add(Calendar.DATE, -2);
			break;
		case (Calendar.THURSDAY):
			gc.add(Calendar.DATE, -3);
			break;
		case (Calendar.FRIDAY):
			gc.add(Calendar.DATE, -4);
			break;
		case (Calendar.SATURDAY):
			gc.add(Calendar.DATE, -5);
			break;
		}
		return gc;
	}

	/**
	 * 取得指定日期的所处星期的最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Date类型 指定日期的所处星期的最后一天
	 */
	public static Date getLastDayOfWeek(Date date) {
		/**
		 * 详细设计： 1.如果date是星期日，则加6天 2.如果date是星期一，则加5天 3.如果date是星期二，则加4天
		 * 4.如果date是星期三，则加3天 5.如果date是星期四，则加2天 6.如果date是星期五，则加1天
		 * 7.如果date是星期六，则加0天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		switch (gc.get(Calendar.DAY_OF_WEEK)) {
		case (Calendar.SUNDAY):
			gc.add(Calendar.DATE, 6);
			break;
		case (Calendar.MONDAY):
			gc.add(Calendar.DATE, 5);
			break;
		case (Calendar.TUESDAY):
			gc.add(Calendar.DATE, 4);
			break;
		case (Calendar.WEDNESDAY):
			gc.add(Calendar.DATE, 3);
			break;
		case (Calendar.THURSDAY):
			gc.add(Calendar.DATE, 2);
			break;
		case (Calendar.FRIDAY):
			gc.add(Calendar.DATE, 1);
			break;
		case (Calendar.SATURDAY):
			gc.add(Calendar.DATE, 0);
			break;
		}
		return gc.getTime();
	}

	/**
	 * 取得指定日期的所处星期的第一天(中式)
	 * 
	 * @param date指定日期
	 *            。
	 * @return 指定日期的所处星期的第一天
	 */
	public static Date getFirstDayOfWeek_CH(Date date) {
		/**
		 * 详细设计： 1.如果date是星期日，则减0天 2.如果date是星期一，则减1天 3.如果date是星期二，则减2天
		 * 4.如果date是星期三，则减3天 5.如果date是星期四，则减4天 6.如果date是星期五，则减5天
		 * 7.如果date是星期六，则减6天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		switch (gc.get(Calendar.DAY_OF_WEEK)) {
		case (Calendar.SUNDAY):
			gc.add(Calendar.DATE, -6);
			break;
		case (Calendar.MONDAY):
			gc.add(Calendar.DATE, 0);
			break;
		case (Calendar.TUESDAY):
			gc.add(Calendar.DATE, -1);
			break;
		case (Calendar.WEDNESDAY):
			gc.add(Calendar.DATE, -2);
			break;
		case (Calendar.THURSDAY):
			gc.add(Calendar.DATE, -3);
			break;
		case (Calendar.FRIDAY):
			gc.add(Calendar.DATE, -4);
			break;
		case (Calendar.SATURDAY):
			gc.add(Calendar.DATE, -5);
			break;
		}
		return gc.getTime();
	}
	
	/**
	 * 取得指定日期的所处星期的最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Date类型 指定日期的所处星期的最后一天
	 */
	public static Date getLastDayOfWeek_CH(Date date) {
		/**
		 * 详细设计： 1.如果date是星期日，则加6天 2.如果date是星期一，则加5天 3.如果date是星期二，则加4天
		 * 4.如果date是星期三，则加3天 5.如果date是星期四，则加2天 6.如果date是星期五，则加1天
		 * 7.如果date是星期六，则加0天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		switch (gc.get(Calendar.DAY_OF_WEEK)) {
		case (Calendar.SUNDAY):
			gc.add(Calendar.DATE, 0);
			break;
		case (Calendar.MONDAY):
			gc.add(Calendar.DATE, 6);
			break;
		case (Calendar.TUESDAY):
			gc.add(Calendar.DATE, 5);
			break;
		case (Calendar.WEDNESDAY):
			gc.add(Calendar.DATE, 4);
			break;
		case (Calendar.THURSDAY):
			gc.add(Calendar.DATE, 3);
			break;
		case (Calendar.FRIDAY):
			gc.add(Calendar.DATE, 2);
			break;
		case (Calendar.SATURDAY):
			gc.add(Calendar.DATE, 1);
			break;
		}
		return gc.getTime();
	}
	
	/**
	 * 取得指定日期的下一个星期的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Date类型 指定日期的下一个星期的第一天
	 */
	public static Date getFirstDayOfNextWeek(Date date) {
		/**
		 * 详细设计： 1.调用getNextWeek设置当前时间 2.以1为基础，调用getFirstDayOfWeek
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.setTime(DateUtil.getNextWeek(gc.getTime()));
		gc.setTime(DateUtil.getFirstDayOfWeek(gc.getTime()));
		return gc.getTime();
	}

	/**
	 * 取得指定日期的下一个星期的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Calendar类型 指定日期的下一个星期的第一天
	 */
	public static Calendar getFirstDayOfNextWeek(Calendar gc) {
		/**
		 * 详细设计： 1.调用getNextWeek设置当前时间 2.以1为基础，调用getFirstDayOfWeek
		 */
		gc.setTime(DateUtil.getNextWeek(gc.getTime()));
		gc.setTime(DateUtil.getFirstDayOfWeek(gc.getTime()));
		return gc;
	}

	/**
	 * 取得指定日期的下一个星期的最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一个星期的最后一天
	 */
	public static Date getLastDayOfNextWeek(Date date) {
		/**
		 * 详细设计： 1.调用getNextWeek设置当前时间 2.以1为基础，调用getLastDayOfWeek
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.setTime(DateUtil.getNextWeek(gc.getTime()));
		gc.setTime(DateUtil.getLastDayOfWeek(gc.getTime()));
		return gc.getTime();
	}

	/**
	 * 取得指定日期的下一个星期
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一个星期
	 */
	public static Date getNextWeek(Date date) {
		/**
		 * 详细设计： 1.指定日期加7天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, 7);
		return gc.getTime();
	}

	public static Calendar getNextWeek(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期加7天
		 */
		gc.add(Calendar.DATE, 7);
		return gc;
	}

	/**
	 * 取得指定日期的上一个星期
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个星期
	 */
	public static Date getPreviousWeek(Date date) {
		/**
		 * 详细设计： 1.指定日期减7天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, -7);
		return gc.getTime();
	}

	public static Calendar getPreviousWeek(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期减7天
		 */
		gc.add(Calendar.DATE, -7);
		return gc;
	}
	
	/**
	 * 取得指定日期的上一个星期第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个星期第一天
	 */
	public static Date getFirstDayOfPreviousWeek(Date date) {
		/**
		 * 详细设计： 1.指定日期减7天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, -7);
		gc.setTime(DateUtil.getFirstDayOfWeek_CH(gc.getTime()));
		return gc.getTime();
	}

	public static Calendar getFirstDayOfPreviousWeek(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期减7天
		 */
		gc.add(Calendar.DATE, -7);
		gc.setTime(DateUtil.getFirstDayOfWeek_CH(gc.getTime()));
		return gc;
	}

	/**
	 * 取得指定日期的上一个星期最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个星期最后一天
	 */
	public static Date getLastDayOfPreviousWeek(Date date) {
		/**
		 * 详细设计： 1.指定日期减7天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, -7);
		gc.setTime(DateUtil.getLastDayOfWeek_CH(gc.getTime()));
		return gc.getTime();
	}
	
	/***************************************************************************
	 * 获得给定日期所在的星期几
	 * 
	 * @param date
	 * @return 整数类型
	 */
	public static int getWeekForDate(Date date) {
		Calendar a_gc = Calendar.getInstance();
		a_gc.setTime(date);
		return a_gc.get(Calendar.DAY_OF_WEEK) - 1;

	}

	/***************************************************************************
	 * 获得给定日期所在的星期几
	 * 
	 * @param Calendar
	 * @return 整数类型
	 */
	public static int getWeekForDate(Calendar gc) {
		return gc.get(Calendar.DAY_OF_WEEK) - 1;
	}

	// end－－－－－－－－－－－－－－－－－－－与星期有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//

	// －－－－－－－－－－－－－－－－－－－与月份有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//
	/**
	 * 取得指定日期的所处月份的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Date类型指定日期的所处月份的第一天
	 */
	public static Date getFirstDayOfMonth(Date date) {
		/**
		 * 详细设计： 1.设置为1号
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.set(Calendar.DAY_OF_MONTH, 1);
		return gc.getTime();
	}

	/**
	 * 取得指定日期的所处月份的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return Calendar类型 指定日期的所处月份的第一天
	 */
	public static Calendar getFirstDayOfMonth(Calendar gc) {
		/**
		 * 详细设计： 1.设置为1号
		 */
		gc.set(Calendar.DAY_OF_MONTH, 1);
		return gc;
	}

	/**
	 * 取得指定日期的所处月份的最后一天
	 * 
	 * @param date
	 *            指定日期
	 * @return 日期类型 指定日期的所处月份的最后一天
	 */
	public static Date getLastDayOfMonth(Date date) {
		/**
		 * 详细设计： 1.如果date在1月，则为31日 2.如果date在2月，则为28日 3.如果date在3月，则为31日
		 * 4.如果date在4月，则为30日 5.如果date在5月，则为31日 6.如果date在6月，则为30日
		 * 7.如果date在7月，则为31日 8.如果date在8月，则为31日 9.如果date在9月，则为30日
		 * 10.如果date在10月，则为31日 11.如果date在11月，则为30日 12.如果date在12月，则为31日
		 * 1.如果date在闰年的2月，则为29日
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		switch (gc.get(Calendar.MONTH)) {
		case 0:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 1:
			gc.set(Calendar.DAY_OF_MONTH, 28);
			break;
		case 2:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 3:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 4:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 5:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 6:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 7:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 8:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 9:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 10:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 11:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		}
		// 检查闰年
		if ((gc.get(Calendar.MONTH) == Calendar.FEBRUARY) && (isLeapYear(gc.get(Calendar.YEAR)))) {
			gc.set(Calendar.DAY_OF_MONTH, 29);
		}
		return gc.getTime();
	}

	/**
	 * 取得指定日期的所处月份的最后一天
	 * 
	 * @param Calendar
	 *            指定日期日历
	 * @return Calendar类型指定日期的所处月份的最后一天
	 */
	public static Calendar getLastDayOfMonth(Calendar gc) {
		/**
		 * 详细设计： 1.如果date在1月，则为31日 2.如果date在2月，则为28日 3.如果date在3月，则为31日
		 * 4.如果date在4月，则为30日 5.如果date在5月，则为31日 6.如果date在6月，则为30日
		 * 7.如果date在7月，则为31日 8.如果date在8月，则为31日 9.如果date在9月，则为30日
		 * 10.如果date在10月，则为31日 11.如果date在11月，则为30日 12.如果date在12月，则为31日
		 * 1.如果date在闰年的2月，则为29日
		 */
		switch (gc.get(Calendar.MONTH)) {
		case 0:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 1:
			gc.set(Calendar.DAY_OF_MONTH, 28);
			break;
		case 2:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 3:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 4:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 5:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 6:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 7:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 8:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 9:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		case 10:
			gc.set(Calendar.DAY_OF_MONTH, 30);
			break;
		case 11:
			gc.set(Calendar.DAY_OF_MONTH, 31);
			break;
		}
		// 检查闰年
		if ((gc.get(Calendar.MONTH) == Calendar.FEBRUARY) && (isLeapYear(gc.get(Calendar.YEAR)))) {
			gc.set(Calendar.DAY_OF_MONTH, 29);
		}
		return gc;
	}

	/**
	 * 取得指定日期的下一个月的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一个月的第一天
	 */
	public static Date getFirstDayOfNextMonth(Date date) {
		/**
		 * 详细设计： 1.调用getNextMonth设置当前时间 2.以1为基础，调用getFirstDayOfMonth
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.setTime(DateUtil.getNextMonth(gc.getTime()));
		gc.setTime(DateUtil.getFirstDayOfMonth(gc.getTime()));
		return gc.getTime();
	}

	public static Calendar getFirstDayOfNextMonth(Calendar gc) {
		/**
		 * 详细设计： 1.调用getNextMonth设置当前时间 2.以1为基础，调用getFirstDayOfMonth
		 */
		gc.setTime(DateUtil.getNextMonth(gc.getTime()));
		gc.setTime(DateUtil.getFirstDayOfMonth(gc.getTime()));
		return gc;
	}

	/**
	 * 取得指定日期的下一个月的最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一个月的最后一天
	 */
	public static Date getLastDayOfNextMonth(Date date) {
		/**
		 * 详细设计： 1.调用getNextMonth设置当前时间 2.以1为基础，调用getLastDayOfMonth
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.setTime(DateUtil.getNextMonth(gc.getTime()));
		gc.setTime(DateUtil.getLastDayOfMonth(gc.getTime()));
		return gc.getTime();
	}

	/**
	 * 取得指定日期的下一个月
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一个月
	 */
	public static Date getNextMonth(Date date) {
		/**
		 * 详细设计： 1.指定日期的月份加1
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.MONTH, 1);
		return gc.getTime();
	}

	public static Calendar getNextMonth(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期的月份加1
		 */
		gc.add(Calendar.MONTH, 1);
		return gc;
	}

	/**
	 * 取得指定日期的上一个月
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个月
	 */
	public static Date getPreviousMonth(Date date) {
		/**
		 * 详细设计： 1.指定日期的月份减1
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.MONTH, -1);
		return gc.getTime();
	}
	
	public static Calendar getPreviousMonth(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期的月份减1
		 */
		gc.add(Calendar.MONTH, -1);
		return gc;
	}
	
	/**
	 * 取得指定日期的上一个月的第一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个月第一天
	 */
	public static Date getFirstDayOfPreviousMonth(Date date) {
		/**
		 * 详细设计： 1.指定日期的月份减1
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.MONTH, -1);
		gc.setTime(DateUtil.getFirstDayOfMonth(gc.getTime()));
		return gc.getTime();
	}
	
	/**
	 * 取得指定日期的上一个月的最后一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的上一个月最后一天
	 */
	public static Date getLastDayOfPreviousMonth(Date date) {
		/**
		 * 详细设计： 1.指定日期的月份减1
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.MONTH, -1);
		gc.setTime(DateUtil.getLastDayOfMonth(gc.getTime()));
		return gc.getTime();
	}

	// end－－－－－－－－－－－－－－－－－－－与月份有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//

	// －－－－－－－－－－－－－－－－－－－与日期有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//
	/**
	 * 取得指定日期的下一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的下一天
	 */
	public static Date getNextDay(Date date) {
		/**
		 * 详细设计： 1.指定日期加1天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, 1);
		return gc.getTime();
	}

	public static Calendar getNextDay(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期加1天
		 */
		gc.add(Calendar.DATE, 1);
		return gc;
	}

	/**
	 * 取得指定日期的前一天
	 * 
	 * @param date
	 *            指定日期。
	 * @return 指定日期的前一天
	 */
	public static Date getPreviousDay(Date date) {
		/**
		 * 详细设计： 1.指定日期减1天
		 */
		GregorianCalendar gc = (GregorianCalendar) Calendar.getInstance();
		gc.setTime(date);
		gc.add(Calendar.DATE, -1);
		return gc.getTime();
	}

	public static Calendar getPreviousDay(Calendar gc) {
		/**
		 * 详细设计： 1.指定日期减1天
		 */
		gc.add(Calendar.DATE, -1);
		return gc;
	}

	/**
	 * 给定日期类型获得日期所在年
	 */
	public static String getYearForDateTime(Date date) {
		// --yyyy-MM-dd hh:mm
		String str_date = getDateTime(datetimePattern, date).trim();
		return str_date.substring(0, 4);
	}

	/***************************************************************************
	 * 给定日期类型获得日期所在月份
	 * 
	 * @param date
	 * @return
	 */
	public static String getMonthForDateTime(Date date) {
		// --yyyy-MM-dd hh:mm
		String str_date = getDateTime(datetimePattern, date).trim();
		return str_date.substring(5, 7);
	}

	/***************************************************************************
	 * 给定日期类型获得日期所在日
	 * 
	 * @param date
	 * @return
	 */
	public static String getDateForDateTime(Date date) {
		// --yyyy-MM-dd hh:mm
		String str_date = getDateTime(datetimePattern, date).trim();
		return str_date.substring(8, 10);
	}

	/***************************************************************************
	 * 给定日期类型获得日期所在时
	 * 
	 * @param date
	 * @return
	 */
	public static String getHourForDateTime(Date date) {
		// --yyyy-MM-dd hh:mm
		String str_date = getDateTime(datetimePattern, date).trim();
		return str_date.substring(11, 13);
	}

	public static String getMinuteForDateTime(Date date) {
		// --yyyy-MM-dd hh:mm
		String str_date = getDateTime(datetimePattern, date).trim();
		return str_date.substring(14, 16);
	}

	// end－－－－－－－－－－－－－－－－－－与日期有关的方法－－－－－－－－－－－－－－－－－－－－－－－－//

}
