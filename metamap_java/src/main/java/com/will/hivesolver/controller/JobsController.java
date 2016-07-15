package com.will.hivesolver.controller;

import com.will.hivesolver.entity.Execution;
import com.will.hivesolver.service.ETLService;
import com.will.hivesolver.util.JsonUtil;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;
import javax.ws.rs.core.MediaType;

@Controller
@RequestMapping("jobs")
public class JobsController {
    
    private static Logger log = LoggerFactory.getLogger(JobsController.class);

    @Resource
    ETLService etlService;

    @RequestMapping(value = "getExec",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getExec(int id) {
        try {
            Execution execution = etlService.getExecutionById(id);
            return JsonUtil.writeValueAsString(execution);
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
            return "error";
        }
    }

}
