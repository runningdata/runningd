package com.will.hivesolver.util;

import java.text.ParseException;

/**
 * Common used functions mapping to ETL Script.
 *
 * Created by will on 16-7-8.
 */
public class ETLUtils {
    /**
     *
     * @param delta
     * @return "20160909"
     * @throws ParseException
     */
    public String getDateKeyFromNow(Integer delta) throws ParseException {
        return DateUtil.getDateFromNowByFmt(delta, ETLConsts.DATEKEY_FORMAT);
    }

    /**
     *
     * @param date
     * @param delta
     * @return  "20160909"
     * @throws ParseException
     */
    public String getDateKey(String date, Integer delta) throws ParseException {
        return DateUtil.getDateStrByFmt(date, delta, ETLConsts.DATEKEY_FORMAT);
    }

    /**
     *
     * @param delta
     * @return "2016-09-09"
     * @throws ParseException
     */
    public String getDateFromNow(Integer delta) throws ParseException {
        return DateUtil.getDateFromNowByFmt(delta, ETLConsts.DATE_FORMAT);
    }

    /**
     *
     * @param date
     * @param delta
     * @return "2016-09-09"
     * @throws ParseException
     */
    public String getDate(String date, Integer delta) throws ParseException {
        return DateUtil.getDateStrByFmt(date, delta, ETLConsts.DATE_FORMAT);
    }

    /**
     *
     * @param date "2016-09-09"
     * @return "20160909"
     * @throws ParseException
     */
    public String date2DateKey(String date) throws ParseException {
        return date.replace("-","");
    }

    /**
     *
     * @param datekey "2016-09-09"
     * @return "20160909"
     * @throws ParseException
     */
    public String dateKey2Date(String datekey) throws ParseException {
        StringBuffer sb = new StringBuffer();
        sb.append(datekey.substring(0, 4)).append(datekey.substring(5, 2)).append(datekey.substring(8, 2));
        return sb.toString();
    }
}
