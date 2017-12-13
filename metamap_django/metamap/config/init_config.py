
with open('/etc/runningd.conf') as f:
    cc = f.read()
    print cc
    import json
    result = json.loads(cc)