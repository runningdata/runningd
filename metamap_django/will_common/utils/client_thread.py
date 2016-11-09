# -*- coding: utf-8 -*
'''
created by will 
'''
from subprocess import Popen, PIPE
from time import sleep
from nbstreamreader import NonBlockingStreamReader as NBSR, UnexpectedEndOfStream

# run the shell as a subprocess:
p = Popen(['python', 'shell.py'],
          stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
# wrap p.stdout with a NonBlockingStreamReader object:
try:
    nbsr = NBSR(p.stdout)
    # issue command:
    p.stdin.write('command\n')
    # get the output
    while True:
        output = nbsr.readline()
        if output == 'ending..':
            print '[No more data]'
            break
        print output
except UnexpectedEndOfStream:
    print('over')
else:
    pass

print('ddddddddddd %s ' % p.returncode)
if p.returncode == 0:
    print 'process successed'
else:
    print 'process error'
