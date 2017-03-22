import re


def check_email(email):
    pattern = '^[a-z0-9]+([._\\-]*[a-z0-9])*@([a-z0-9]+[-a-z0-9]*[a-z0-9]+.){1,63}[a-z0-9]+$'
    if re.match(pattern, email, flags=0):
        return True
    else:
        return False