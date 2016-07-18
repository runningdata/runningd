package com.will.hivesolver.util;

import com.will.hivesolver.entity.Execution;
import com.will.hivesolver.util.enums.ExecutionStatusEnum;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.PumpStreamHandler;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileOutputStream;
import java.util.Date;

/**
 * Created by will on 16-7-14.
 */
public class ETLTask implements Runnable{
    private static Logger log = LoggerFactory.getLogger(ETLTask.class);

    private String file;

    private File out;

    private Execution exec;

    public ETLTask(String file, Execution execution) {
        this.file = file;
        this.out = new File(execution.getLogLocation());
        this.exec = execution;
    }

    @Override
    public void run() {
        try {
//            ExecutionRepository executionRepository = (ExecutionRepository) ContextUtil.getBean("executionRepository");
            FileOutputStream baos = null;
            try {
                String line = "hive -f " + file;
                CommandLine cmdLine = CommandLine.parse(line);
                DefaultExecutor executor = new DefaultExecutor();
                executor.setExitValue(0);
                baos = new FileOutputStream(out, true);
                executor.setStreamHandler(new PumpStreamHandler(baos, baos));
                int exitValue = executor.execute(cmdLine);
                FileUtils.writeStringToFile(out, file + " job done\n", "utf8", true);
                exec.setStatus(ExecutionStatusEnum.DONE.get());
            } catch (Exception e ) {
                exec.setStatus(ExecutionStatusEnum.FAILED.get());
                throw new Exception(e);
            } finally {
                exec.setEndTime(new Date());
                log.info(JsonUtil.writeValueAsString(exec));
//                executionRepository.save(exec);
                if (baos != null) {
                    baos.close();
                }
            }
        } catch (Exception e) {
            log.error(ExceptionUtils.getFullStackTrace(e), e);
        }
    }
}
