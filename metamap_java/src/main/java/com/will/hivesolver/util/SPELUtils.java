package com.will.hivesolver.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.common.TemplateParserContext;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

/**
 * Created by root on 16-7-8.
 */
public class SPELUtils {
    private static Logger log = LoggerFactory.getLogger(SPELUtils.class);

    public static final ExpressionParser parser = new SpelExpressionParser();
    public static final StandardEvaluationContext context = new StandardEvaluationContext(new ETLUtils());

    static {
        try {
            context.registerFunction("get_datekey",
                    ETLUtils.class.getDeclaredMethod("getDateKey", String.class, Integer.class));
            context.registerFunction("get_nowdatekey",
                    ETLUtils.class.getDeclaredMethod("getDateKeyFromNow", Integer.class));
            context.registerFunction("get_date",
                    ETLUtils.class.getDeclaredMethod("getDate", String.class, Integer.class));
            context.registerFunction("get_nowdate",
                    ETLUtils.class.getDeclaredMethod("getDateFromNow", Integer.class));
        } catch (NoSuchMethodException e) {
            log.error("Error when resigter custom method to Sping EL Context");
        }
    }

    public static String getRenderELTemplate(String content) {
        String getDateKeyStr = parser.parseExpression(content,
                new TemplateParserContext()).getValue(context, String.class);
        System.out.println(getDateKeyStr);
        return getDateKeyStr;
    }
}
