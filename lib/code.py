from binascii import hexlify
from random import random
from hashlib import sha1
from time import time


# Generate random code base on time
def get_random_code():
    # codes are randomised due to time not repeatable
    code = []
    text = 'abcdefghij'
    for i in str(int(time() * 1000)):
        code.append(text[int(i)])
        if random() < 0.5:
            code[-1] = code[-1].upper()
    return ''.join(code)


# Generate the code base on SHA-1
def get_code(byte):
    if not isinstance(byte, bytes):
        byte = str(byte).encode('utf-8')
    return hexlify(sha1(byte).digest()).decode('utf-8')
