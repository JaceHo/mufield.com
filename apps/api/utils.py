import random
import math
from compressor.cache import get_hexdigest

__author__ = 'hippo'

loop = '0123456789abcdefghijklmnopqrstuvwxyz'


def int_36_str(number):  # 36位映射模板
    a = []
    while number != 0:
        a.append(loop[number % 36])
        a.append(random.choice(loop))
        number = math.floor(number / 36)
    return ''.join(a)


