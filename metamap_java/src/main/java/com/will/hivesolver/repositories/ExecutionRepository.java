package com.will.hivesolver.repositories;

import com.will.hivesolver.entity.Execution;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Set;

/**
 * Created by will on 16-7-13.
 */
public interface ExecutionRepository extends JpaRepository<Execution, Integer>{
    public Set<Execution> findByJobId(int id);
}
