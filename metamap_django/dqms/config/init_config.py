with open('/etc/running_dqms.conf') as f:
    cc = f.read()
    print cc
    import json
    result = json.loads(cc)