package com.will.hivesolver.utils;

import junit.framework.TestCase;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.ExecuteWatchdog;
import org.apache.commons.exec.PumpStreamHandler;
import org.apache.commons.io.output.ByteArrayOutputStream;
import org.junit.Test;

import java.io.*;
import java.util.concurrent.*;

/**
 * Created by will on 16-7-14.
 */
public class ExecTest extends TestCase {
    ExecutorService executorService = Executors.newFixedThreadPool(3);

    String CMD = "sh /usr/local/metamap/metamap_express/test.sh > /usr/local/metamap/metamap_express/test.sh.log 2>&1";

    class ExecTask implements Callable<String> {

        @Override
        public String call() throws Exception {
            FileOutputStream baos = null;
            try {
                String line = CMD;
                CommandLine cmdLine = CommandLine.parse(line);
                DefaultExecutor executor = new DefaultExecutor();
                executor.setExitValue(0);
                ExecuteWatchdog watchdog = new ExecuteWatchdog(60000);
                executor.setWatchdog(watchdog);
                baos = new FileOutputStream(new File("/usr/local/metamap/metamap_express/test.sh.log"));
                executor.setStreamHandler(new PumpStreamHandler(baos, baos));
                int exitValue = executor.execute(cmdLine);
            } finally {
                if (baos != null) {
                    baos.close();
                }
            }

            return "";
        }
    }

    class RuntimeTask implements Callable<String> {

        @Override
        public String call() throws Exception {
            Process exec = Runtime.getRuntime().exec("sh /usr/local/metamap/metamap_express/test.sh");
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(exec.getInputStream()));
            String s;
            while((s=bufferedReader.readLine()) != null) {
//                System.out.println(s);
            }
            exec.waitFor();

            return "";
        }
    }

    @Test
    public void testCommonExec() throws ExecutionException, InterruptedException {

        Future<String> task = executorService.submit(new ExecTask());
//        System.out.println(task.get());
        System.out.println("done");
        System.out.println(task.get());
    }

    @Test
    public void testRuntime() throws IOException, InterruptedException, ExecutionException {
        Future<String> task = executorService.submit(new RuntimeTask());
//        System.out.println(task.get());
        System.out.println("done");
        System.out.println(task.get());
    }
}
