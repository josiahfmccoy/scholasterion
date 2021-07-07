import base64
from random import randint


def make_uid(n=64**8):
    uid = base64.b64encode(bytes(str(randint(1, n)), encoding='ascii'))
    return uid.decode('ascii')
