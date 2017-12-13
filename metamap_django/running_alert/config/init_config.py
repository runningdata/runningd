
with open('/etc/running_alert.conf') as f:
    cc = f.read()
    print cc
    import json
    result = json.loads(cc)