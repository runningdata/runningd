package com.will.hivesolver.controller;

import com.will.hivesolver.service.HiveMetaService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;

@Controller
@RequestMapping("meta")
public class HiveMetaController {
    
    private static Logger log = LoggerFactory.getLogger(HiveMetaController.class);

    @Resource(name = "hiveMetaService")
    private HiveMetaService hiveMetaService;

    @RequestMapping(method = RequestMethod.GET)
    public @ResponseBody Object ping() {
        return "pang";
    }

}
