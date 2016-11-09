# -*- coding: utf-8 -*
'''
created by will 
'''
import sys
import time
threshold = 3
tmp = 1
while True:
    # s = raw_input("Enter command: ")
    s = 's'
    time.sleep(1)
    print "You entered: {}".format(s)
    sys.stdout.flush()
    tmp += 1
    print tmp
    if tmp == threshold:
        break