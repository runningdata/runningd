package com.will.hivesolver.controller;

import com.will.hivesolver.entity.ColMeta;
import com.will.hivesolver.service.HiveMetaService;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.PumpStreamHandler;
import org.apache.commons.io.output.ByteArrayOutputStream;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;
import javax.ws.rs.Path;
import java.io.IOException;
import java.util.List;

@Controller
@RequestMapping("/hivemeta")
public class HiveMetaController {
    
    private static Logger log = LoggerFactory.getLogger(HiveMetaController.class);

    @Resource(name = "hiveMetaService")
    private HiveMetaService hiveMetaService;

    @RequestMapping(method = RequestMethod.GET)
    public @ResponseBody Object ping() {
        return "pang";
    }

    @RequestMapping(value = "/whoami",method = RequestMethod.GET)
    public @ResponseBody Object whoami() {
        String cmdStr = "whoami";
        try {
            final CommandLine cmdLine = CommandLine.parse(cmdStr);

            DefaultExecutor executor = new DefaultExecutor();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            executor.setStreamHandler(new PumpStreamHandler(baos, baos));

            executor.setExitValue(0);
            int exitValue = executor.execute(cmdLine);
            return baos.toString();
        } catch (IOException e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
        }

        return cmdStr;
    }

    @RequestMapping(value = "/prepare",method = RequestMethod.GET)
    public @ResponseBody Object prepare() {
        String cmdStr = "fail";
        try {
            return hiveMetaService.prepareColMeta();
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
        }

        return cmdStr;
    }

    @RequestMapping(value = "/search",method = RequestMethod.GET)
    public @ResponseBody Object search(String colName) {
        try {
            return hiveMetaService.search(colName);
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
        }

        return null;
    }

}
