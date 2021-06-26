


from binascii import hexlify
from random import random
from hashlib import sha1
from time import time


def get_random_code():
    code = []
    text = 'abcdefghij'
    for i in str(int(time() * 1000)):
        code.append(text[int(i)])
        if random() < 0.5:
            code[-1] = code[-1].upper()

    return ''.join(code)


def get_code(byte):
    if not isinstance(byte, bytes):
        byte = str(byte).encode('utf-8')
    return hexlify(sha1(byte).digest()).decode('utf-8')


def get_file_code(file):
    file = open(file, 'rb')
    code = get_code(file.read())
    file.close()
    return code
