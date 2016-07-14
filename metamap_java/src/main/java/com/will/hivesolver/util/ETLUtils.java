package com.will.hivesolver.util;

import java.text.ParseException;

/**
 * Common used functions mapping to ETL Script.
 *
 * Created by will on 16-7-8.
 */
public class ETLUtils {
    public String getDateKeyFromNow(Integer delta) throws ParseException {
        return DateUtil.getDateKeyStrFromNow(delta);
    }

    public String getDateKey(String date, Integer delta) throws ParseException {
        return DateUtil.getDateKeyStr(date, delta);
    }

    public String getDateFromNow(Integer delta) throws ParseException {
        return DateUtil.getDateKeyStrFromNowFormat(delta, "yyyy-MM-dd");
    }

    public String getDate(String date, Integer delta) throws ParseException {
        return DateUtil.getDateKeyStrFormat(date, delta, "yyyy-MM-dd");
    }
}
