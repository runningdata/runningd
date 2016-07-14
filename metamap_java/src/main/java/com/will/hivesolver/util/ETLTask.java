package com.will.hivesolver.util;

import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.ExecuteWatchdog;
import org.apache.commons.exec.PumpStreamHandler;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

/**
 * Created by will on 16-7-14.
 */
public class ETLTask implements Runnable{
    private static Logger log = LoggerFactory.getLogger(ETLTask.class);

    private String file;

    private File out;

    public ETLTask(String file, String outFile) {
        this.file = file;
        this.out = new File(outFile);
    }

    @Override
    public void run() {
        try {
            FileOutputStream baos = null;
            try {
                String line = "hive -f " + file;
                CommandLine cmdLine = CommandLine.parse(line);
                DefaultExecutor executor = new DefaultExecutor();
                executor.setExitValue(0);
//                ExecuteWatchdog watchdog = new ExecuteWatchdog(60000);
//                executor.setWatchdog(watchdog);
                baos = new FileOutputStream(out, true);
                executor.setStreamHandler(new PumpStreamHandler(baos, baos));
                int exitValue = executor.execute(cmdLine);
                FileUtils.writeStringToFile(out, file + " job done\n", "utf8", true);
            } finally {
                if (baos != null) {
                    baos.close();
                }
            }
        } catch (IOException e) {
            log.error("Error when processing hive ETL: " + file);
            e.printStackTrace();
        }
    }
}
