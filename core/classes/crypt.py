import base64
import hashlib
import hmac
import os

from core.common.config import *


def _encrypt(key: bytes | bytearray, data: bytes | bytearray) -> bytes:
    l = len(key)
    s = list(range(256))
    j = 0

    for i in range(256):
        j = (j + s[i] + key[i % l]) % 256
        s[i], s[j] = s[j], s[i]

    o = []
    i = 0
    j = 0

    for c in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]

        o.append(c ^ s[(s[i] + s[j]) % 256])

    return bytes(o)


class RosCrypt:
    sess_key: str
    sess_ticket: str
    acct_ticket: str

    xor: bytes
    hash: bytes

    def __init__(self) -> None:
        dec = base64.b64decode(ROS_KEY)
        key = dec[1:33]

        self.xor = _encrypt(key, dec[33:49])
        self.hash = _encrypt(key, dec[49:65])

    def encrypt(self, data: bytes) -> bytes:
        r = bytearray(os.urandom(16))
        o = bytearray()
        k = base64.b64decode(self.sess_key)

        for i in range(16):
            o.append(r[i] ^ self.xor[i])
            r[i] ^= k[i]

        o += _encrypt(r, data)
        h = bytearray(o)
        h += self.hash
        h = hmac.HMAC(r, bytes(h), hashlib.sha1).digest()
        o += h

        return bytes(o)

    def decrypt(self, data: bytes) -> bytes:
        r = bytearray(16)
        o = bytearray()
        k = base64.b64decode(self.sess_key)

        for i in range(16):
            r[i] = data[i] ^ self.xor[i]
            r[i] ^= k[i]

        a = data[16:20]
        b = _encrypt(r, a)
        b = (b[0] << 24) + (b[1] << 16) + (b[2] << 8) + b[1] + 20
        o += a
        t = 20

        while t < len(data):
            e = min(len(data), t + b)
            e -= 20
            o += data[t:e]
            t += b

        return _encrypt(r, o)

    def http_headers(self, method: str, path: str) -> dict[str, str]:
        r = bytearray(16)
        k = base64.b64decode(self.sess_key)
        c = base64.b64encode(os.urandom(8))

        for i in range(16):
            r[i] = k[i] ^ self.xor[i]

        h = b""
        h += method.encode()
        h += b"\x00"
        h += path.encode()
        h += b"\x00"
        h += b"239"
        h += b"\x00"
        h += self.sess_ticket.encode()
        h += b"\x00"
        h += c
        h += b"\x00"
        h += self.hash

        u = f"e=1,t=gta5,p=pcros,v={ROS_VERSION}"
        b = bytearray(len(u) + 4)

        for i in range(4):
            b[i] = 0xCD

        for i in range(len(u)):
            b[i + 4] = ord(u[i]) ^ 0xCD

        u = base64.b64encode(b).decode()
        d = {}

        if method == "GET":
            d["scs-ticket"] = self.acct_ticket

        if method == "POST":
            d["content-type"] = "application/x-www-form-urlencoded; charset=utf-8"

        d["user-agent"] = f"ros {u}"
        d["ros-securityflags"] = "239"
        d["ros-sessionticket"] = self.sess_ticket
        d["ros-challenge"] = c.decode()
        d["ros-headershmac"] = base64.b64encode(hmac.HMAC(r, bytes(h), hashlib.sha1).digest()).decode()

        return d
