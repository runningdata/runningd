package com.will.hivesolver.util;

import java.text.ParseException;

/**
 * Common used functions mapping to ETL Script.
 *
 * Created by will on 16-7-8.
 */
public class ETLUtils {
    public String getDateKeyStrFromNow(Integer delta) throws ParseException {
        return DateUtil.getDateKeyStrFromNow(delta);
    }

    public String getDateKeyStr(String date, Integer delta) throws ParseException {
        return DateUtil.getDateKeyStr(date, delta);
    }

    public String getDateKeyStrFromNowFormat(Integer delta, String format) throws ParseException {
        return DateUtil.getDateKeyStrFromNowFormat(delta, format);
    }

    public String getDateKeyStrFormat(String date, Integer delta, String format) throws ParseException {
        return DateUtil.getDateKeyStrFormat(date, delta, format);
    }
}
