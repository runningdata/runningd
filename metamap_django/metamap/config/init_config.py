import json

with open('/etc/runningd.conf') as f:
    cc = f.read()
    print cc
    result = json.loads(cc)
    print result