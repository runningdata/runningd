import base64
from Crypto.Cipher import AES

from metamap_django import settings

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

cc = AES.new(settings.PUSH_KEY)


def encrpt_msg(msg):
    print cc.encrypt(pad(msg))
    return base64.b64encode(cc.encrypt(pad(msg)))


def decrpt_msg(msg):
    result2 = base64.b64decode(msg)
    decrypted = unpad(cc.decrypt(result2))
    return decrypted

print decrpt_msg('PWy9rKUlzFLGO8Ry6v368w==')