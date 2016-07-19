package com.will.hivesolver.controller;

import com.will.exception.MetaException;
import com.will.hivesolver.entity.ETL;
import com.will.hivesolver.service.ETLService;
import com.will.hivesolver.util.JsonUtil;
import com.will.hivesolver.util.ResultBean;
import com.will.hivesolver.util.ResultBean.ResultStatus;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.TypeMismatchException;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;
import javax.ws.rs.core.MediaType;

@Controller
@RequestMapping("etl")
public class ETLController {
    
    private static Logger log = LoggerFactory.getLogger(ETLController.class);

    @Resource(name = "etlService")
    private ETLService etlService;

    @RequestMapping(value = "save",method = RequestMethod.POST, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object addETL(ETL etl) throws Exception{
        etl.setAuthor("will");
        etlService.addETL(etl);
        return "{\"message\" :\"success\"}";
    }

    @RequestMapping(value = "execETLScript",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object execETLScript(int id) {
        try {
            return JsonUtil.writeValueAsString(etlService.execETLScript(id));
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

    @RequestMapping(value = "generateJobScript",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object generateJobScript() {
        try {
            return JsonUtil.writeValueAsString(etlService.generateAzkabanDAG());
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

    @RequestMapping(value = "getMermaidById",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getMermaid(int id) {
        try {
            return JsonUtil.writeValueAsString(etlService.getETLMermaid(id));
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

    @RequestMapping(value = "getMermaid",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getMermaid(String tblName) {
        try {
            return JsonUtil.writeValueAsString(etlService.getETLMermaid(tblName));
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

    @RequestMapping(value = "getETL",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getETLById(int id) {
        try {
            return JsonUtil.writeValueAsString(etlService.getETLById(id));
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

    @RequestMapping(value = "getAll",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getAllETLs() {
        try {
            return JsonUtil.writeValueAsString(etlService.allETL());
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
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
