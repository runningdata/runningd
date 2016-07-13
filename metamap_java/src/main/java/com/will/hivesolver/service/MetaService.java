package com.will.hivesolver.service;

import com.will.hivesolver.entity.Meta;
import com.will.hivesolver.repositories.MetaRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

@Service("metaService")
public class MetaService {

    private static Logger log = LoggerFactory.getLogger(MetaService.class);
    
    @Resource
    MetaRepository metaRepository;

    public void save(Meta meta) {
        metaRepository.save(meta);
    }

    public Meta getById(int id) {
        return metaRepository.findOne(id);
    }

    public List<Meta> getAll() {
        return metaRepository.findAll();
    }

    public String deleteForever(int id) {
        metaRepository.delete(id);
        return "success";
    }
}
