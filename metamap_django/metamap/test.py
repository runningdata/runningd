import base64
import urllib2
from Crypto.Cipher import AES


PUSH_URL = 'https://advert.jianlc.com/sendMessage.shtml?mobileNo=%s&content=%s'
PUSH_KEY = '&OKY%~!$^G*JRRF^'

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]
cc = AES.new(PUSH_KEY)
def encrpt_msg(msg):
    if isinstance(msg, unicode):
        msg_ = msg.encode("utf8")
    # elif isinstance(msg, int) or isinstance(msg, long):
    #     msg_ = str(msg)
    else:
        msg_ = str(msg)
    return base64.b64encode(cc.encrypt(pad(msg_)))

def push_msg_tophone(phone, msg):
    msg_ = PUSH_URL % (encrpt_msg(phone), encrpt_msg(msg))
    req = urllib2.Request(msg_)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
    httpHandler = urllib2.HTTPHandler(debuglevel=1)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
    opener = urllib2.build_opener(httpHandler, httpsHandler)
    urllib2.install_opener(opener)
    resp = urllib2.urlopen(req)
    if resp.getcode() == 200:
        print resp.read()
        return 'push phone success'
    else:
        return 'error', resp.read()


push_msg_tophone('15201976096', 'hdfs usage')