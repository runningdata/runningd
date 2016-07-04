package com.will.hivesolver.controller;

import java.io.IOException;
import java.io.InputStream;

import javax.annotation.Resource;
import javax.ws.rs.core.MediaType;

import com.will.hivesolver.entity.ETL;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.TypeMismatchException;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import com.will.exception.MetaException;
import com.will.hivesolver.entity.User;
import com.will.hivesolver.service.HiveMetaService;
import com.will.hivesolver.util.PageBean;
import com.will.hivesolver.util.ResultBean;
import com.will.hivesolver.util.ResultBean.ResultStatus;

@Controller
@RequestMapping("meta")
public class HiveMetaController {
    
    private static Logger log = LoggerFactory.getLogger(HiveMetaController.class);

    @Resource(name = "hiveMetaService")
    private HiveMetaService hiveMetaService;

    @RequestMapping(method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object ping(String sql) {
        return "{\"pang\" :\"" + sql + "\"}";
    }

    @RequestMapping(value = "etl",method = RequestMethod.GET)
    public @ResponseBody Object etl(ETL etl) {
        return "etl authro: " + etl.getAuthor();
    }

    @RequestMapping("detail/user/{userId}")
    public @ResponseBody Object getUserDetail(@PathVariable String sql) {
        InputStream input = HiveMetaController.class.getClassLoader().getResourceAsStream("all.sql");
        try {
            for (String str : IOUtils.readLines(input, "utf8")) {
                sql +=str;
            }
        } catch (IOException e) {
            log.error("error hadppens : " + e.getMessage());
        }
        log.debug("sql is " + sql);
        ResultBean<User> resultBean = new ResultBean<User>();

        return hiveMetaService.executeSql(sql);
//        if (result == null) {
//            resultBean.setStatus(ResultStatus.FAIL);
//            resultBean.setDescription("未查询到数据");
//        } else {
//            resultBean.setStatus(ResultStatus.SUCCESS);
//            resultBean.setResult(result);
//        }
//
//        return resultBean;
    }

    @RequestMapping("detail/invest/{userId}")
    public @ResponseBody Object getInvestDetail(@PathVariable Long userId,
            @RequestParam(defaultValue = "1") Integer pageIndex,
            @RequestParam(defaultValue = "15") Integer pageSize) {
        return null;
    }

    @RequestMapping("detail/money/{userId}")
    public @ResponseBody Object getMoneyDetail(@PathVariable Long userId,
            @RequestParam(defaultValue = "1") Integer pageIndex,
            @RequestParam(defaultValue = "15") Integer pageSize) {
        ResultBean<PageBean> resultBean = new ResultBean<PageBean>();
        return resultBean;
    }

    public @ResponseBody Object runtimeExceptionHandler(Exception e) {
        ResultBean<String> resultBean = new ResultBean<String>();
        resultBean.setStatus(ResultStatus.ERROR);
        if (e instanceof MetaException) {
            resultBean.setDescription(e.getLocalizedMessage());
        } else if (e instanceof TypeMismatchException) {
            resultBean.setDescription("参数类型错误！");
        } else {
            resultBean.setDescription("未知错误...");
        }
        return resultBean;
    }
}
