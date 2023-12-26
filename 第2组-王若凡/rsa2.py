# -*- coding: utf-8 -*-
# @Time : 2022/4/2 23:00
# @Author : cheney
# @File : rsa.py
# @Software: PyCharm
# @Site: www.cheney.cc


import random
from math import sqrt
import base64

PrivateKe = [int, int]
PublicKey = [int, int]


def __miller_rabin(p: int) -> bool:
    """
    miller_rabin算法素性检测，# https://blog.csdn.net/m0_46530662/article/details/121752790
    :param p: 要判断的数
    :return: 是否为素数，T/F
    """
    if p == 1: return False
    if p == 2: return True
    if p % 2 == 0: return False
    m, k, = p - 1, 0
    while m % 2 == 0:
        m, k = m // 2, k + 1
    a = random.randint(2, p - 1)
    x = pow(a, m, p)
    if x == 1 or x == p - 1: return True
    while k > 1:
        x = pow(x, 2, p)
        if x == 1: return False
        if x == p - 1: return True
        k -= 1
    return False


def __is_prime_m(p: int, r: int = 40):
    """
    多次调用miller_rabin算法判断
    :param p: 要判断的数
    :param r: 循环r 次数
    :return:
    """
    for i in range(r):
        if not __miller_rabin(p):
            return False
    return True


def __is_prime(n: int) -> bool:
    """
    优化后的素数判定函数 https://www.jb51.net/article/208982.htm
    :param n: 要判断的数字
    :return: True or False
    """
    # 先将数分为三类， 小于等于1，大于1小于5，和大于等于5
    # 非整数统统不是素数
    if not isinstance(n, int): return False
    # 小于1等于的都不是素数
    if n <= 1:
        return False
    # 大于1小于5
    elif n == 2 or n == 3:
        return True
    # 大于等于5
    elif n >= 5:
        # 先判断是否在6的附近
        if n % 6 == 5 or n % 6 == 1:
            # 再判断是否可以将2除尽
            # 可以的话不是素数
            if n % 2 == 0:
                return False
            else:
                # 不可除尽2，直接跳过所有偶数
                for i in range(3, int(sqrt(n) + 1), 2):
                    if n % i == 0: return False
                # 经过筛选即为素数
                return True
        # 不在6的附近不是素数
        else:
            return False


def __get_prime(nbits: int):
    """
    获得约等于给定位数的一个素数
    :param nbits: 位数
    :return:
    """
    while True:
        _prime = random.randint(2 ** (nbits - 1), 2 ** (nbits + 0))  # 下限越大，加密越安全，此处考虑计算时间，取值较小
        if __is_prime_m(_prime):
            return _prime


def __ex_gcd(a, b):
    """
    扩展欧几里德算法求模反元素d
    所谓"模反元素"就是指有一个整数d，可以使得a被b除的余数为1。
    :param a:
    :param b:
    :return: d ，
    """
    if b == 0:
        return 1, 0
    else:
        q = a // b
        r = a % b
        s, t = __ex_gcd(b, r)
        s, t = t, s - q * t
    return s, t


def __fast_expmod(a, e, n):
    """
    快速幂取模算法
    :param a:
    :param e:
    :param n:
    :return:
    """
    d = 1
    while e != 0:
        if (e & 1) == 1:
            d = (d * a) % n
        e >>= 1
        a = a * a % n
    return d


def newkeys(nbits: int, e: int = 65537):
    """
    - 第一步，随机选择两个不相等的质数p和q。
    - 第二步，计算p和q的乘积n。
    - 第三步，计算n的欧拉函数φ(n)。φ(n) = (p-1)(q-1)
    - 第四步，随机选择一个整数e，条件是1< e < φ(n)，且e与φ(n) 互质。
    - 第五步，计算e对于φ(n)的模反元素d。所谓"模反元素"就是指有一个整数d，可以使得ed被φ(n)除的余数为1。
    - 第六步，将n和e封装成公钥，n和d封装成私钥。
    :param e: e
    :param nbits: 要生成的位数
    :return:
    """
    p = __get_prime(nbits)
    q = __get_prime(nbits)
    # e =   满足 gcd(e,fn)
    while p == q:  # 确保 p != q
        q = __get_prime(nbits)

    N = p * q
    fn = (p - 1) * (q - 1)  # 计算欧拉函数

    """ 计算e对于φ(n)的模反元素d """
    d, _ = __ex_gcd(e, fn)
    while d < 0:
        d = (d + fn) % fn

    # _PublicKey, _PrivateKey = [N, e], [N, d]
    return [N, e], [N, d]


def encrypt(message: str, _pub_key: PublicKey, _coding: str = "utf-8") -> str :
    """
    加密 c = m^e mod n
    :param message: 待加密的信息 str类型
    :param _pub_key: 公钥 即[N, e]
    :param _coding: 编码方式 默认"utf-8"
    :return: 返回密文 list类型 每个元素是
    """
    n, e = _pub_key

    secretText = []
    for item in message.encode(_coding):
        secretText.append(__fast_expmod(item, e, n))

    return str(secretText)


def decrypt(crypto: str, _priv_key: PrivateKe, _coding: str = "utf-8") -> str:
    """
    解密 m = c^d mod n
    :param crypto: 要解密的密文 list格式 （encrypt的返回值）
    :param _priv_key: 私钥 即[N, d]
    :param _coding: 编码方式 默认"utf-8"
    :return: 返str类型的明文
    """
    n, d = _priv_key
    plaintext = []
    for item in list(eval(crypto)):
        plaintext.append(__fast_expmod(item, d, n))

    return bytes(plaintext).decode(_coding)


if __name__ == '__main__':
    import time

    # 获取公钥和密钥
    start_time = int(round(time.time() * 1000000))
    bits_ = 512
    PublicKey, PrivateKey = newkeys(bits_)
    print("位数：", bits_)
    print("获得的公钥：", PublicKey, "\n获得的私钥：", PrivateKey)

    # 加密
    start_time2 = int(round(time.time() * 1000000))
    PlainText = "这是测试用的明文12345abcDEF。/.;.?@!"
    print("\n待加密明文：", PlainText)
    SecretText = encrypt(PlainText, PublicKey)
    # SecretText = encrypt(base64.b64encode(PlainText.encode("utf-8")), PublicKey)
    print("\n加密后密文：", SecretText)

    # 解密
    start_time3 = int(round(time.time() * 1000000))
    PlainText_ = decrypt(SecretText, PrivateKey)
    # print("\n解密后明文：", base64.b64decode(PlainText_).decode("utf-8"))
    print("\n解密后明文：", PlainText_)

    end_time = int(round(time.time() * 1000000))
    print("\n****获得密钥耗时:", (start_time2 - start_time) / 1000, "ms")
    print("********加密耗时:", (start_time3 - start_time2) / 1000, "ms")
    print("********解密耗时:", (end_time - start_time3) / 1000, "ms")
    print("**********共耗时:", (end_time - start_time) / 1000, "ms")
