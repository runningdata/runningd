package com.will.hivesolver.controller;

import com.will.hivesolver.entity.Meta;
import com.will.hivesolver.service.MetaService;
import com.will.hivesolver.util.JsonUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;
import javax.ws.rs.core.MediaType;

@Controller
@RequestMapping("meta")
public class MetaController {
    
    private static Logger log = LoggerFactory.getLogger(MetaController.class);

    @Resource(name = "metaService")
    private MetaService metaService;

    @RequestMapping(value = "save",method = RequestMethod.POST, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object add(Meta meta) {
        metaService.save(meta);
        return "{\"message\" :\"success\"}";
    }

    @RequestMapping(value = "get",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getMetaById(int id) {
        try {
            return JsonUtil.writeValueAsString(metaService.getById(id));
        } catch (Exception e) {
            log.error("something happened when getMetaById");
            return "error";
        }
    }

    @RequestMapping(value = "getAll",method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON)
    public @ResponseBody Object getAll() {
        try {
            return JsonUtil.writeValueAsString(metaService.getAll());
        } catch (Exception e) {
            log.error("something happened when getAllETLs");
            return "error";
        }
    }

}
