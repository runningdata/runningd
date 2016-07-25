# !/usr/bin/env python
# -*- coding:utf-8 -*-
'''
created by will 
'''
import Queue
import logging
import subprocess
import threading
import time, os
from django.utils import timezone
from subprocess import Popen, PIPE

from metamap.models import Executions

from metamap.utils import enums


class WorkManager(object):
    def __init__(self, work_num=1000, thread_num=2):
        self.work_queue = Queue.Queue()
        self.threads = []
        # self.__init_work_queue(work_num)
        self.__init_thread_pool(thread_num)

    """
      初始化线程
    """

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue))

    """
      初始化工作队列
    """

    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            self.add_job(do_job, i)

    """
      添加一项工作入队
    """

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    """
      检查剩余队列任务
    """

    def check_queue(self):
        return self.work_queue.qsize()

    """
      等待所有线程运行完毕
    """

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive(): item.join()


class Work(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            location = ''
            try:
                do, args = self.work_queue.get_nowait()  # 任务异步出队，Queue内部实现了同步机制
                self.logger.info('%s method ' % do)
                self.logger.info('%s find job ....... %s ' % (self.getName(), ''.join(args[0])))
                do(args)
                self.work_queue.task_done()  # 通知系统任务完成
                location = ''.join(args[1])
                execution = Executions.objects.get(logLocation=location)
                execution.end_time = timezone.now
                execution.status = enums['完成']
                execution.save()
            except Queue.Empty:
                time.sleep(3)
            except Exception as e:
                self.logger.error('got error :%s' % str(e))
                break


# 具体要做的任务
def do_job(*args):
    print args
    log = args[0][1]
    command = args[0][0]
    p = Popen([''.join(command)], stdout=open(log, 'a'), stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    p.wait()
    print threading.current_thread(), list(args)


if __name__ == '__main__':
    start = time.time()
    # work_manager = WorkManager(10, 3)
    # work_manager.add_job(do_job, "sh /usr/local/metamap/test.sh")
    # work_manager.add_job(do_job, "sh /usr/local/metamap/test.sh")
    print "doneeeeeeeeeeeeee"
    end = time.time()
    print "cost all time: %s" % (end - start)
