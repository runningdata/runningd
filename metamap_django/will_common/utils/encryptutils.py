import base64
from Crypto.Cipher import AES

from django.conf import settings

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

cc = AES.new(settings.PUSH_KEY)


def encrpt_msg(msg):
    if isinstance(msg, unicode):
        msg_ = msg.encode("utf8")
    # elif isinstance(msg, int) or isinstance(msg, long):
    #     msg_ = str(msg)
    else:
        msg_ = str(msg)
    return base64.b64encode(cc.encrypt(pad(msg_)))


def decrpt_msg(msg):
    result2 = base64.b64decode(msg)
    decrypted = unpad(cc.decrypt(result2))
    return decrypted