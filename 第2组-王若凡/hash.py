# -*- coding: utf-8 -*-
# @Time : 2022/4/14 17:44
# @Author : cheney
# @File : hash.py
# @Software: PyCharm
# @Site: www.cheney.cc

import hashlib


def encrypt(plaintext: str, salt: str = "cug", _coding: str = "utf-8") -> str:
    """
    用hash的方法对原文进行摘要，返回hash值
    :param plaintext: 要进行hash的原文
    :param _coding: 编码方式 默认"utf-8"
    :param salt: 对原文加盐，生成更复杂对hash值。
    :return: 加密的结果(密文)
    """
    # _hash = hashlib.md5()
    # _hash = hashlib.sha1()
    _hash = hashlib.sha256()
    # _hash = hashlib.sha512()

    # 加盐
    plaintext += salt

    # 进行摘要计算
    _hash.update(plaintext.encode(_coding))
    return _hash.hexdigest()


if __name__ == '__main__':
    import hash

    a = "摘要算法又称哈希算法、散列算法。它通过一个函数，把任意长度的数据转换为一个长度固定的数据串（通常用16进制的字符串表示）。"
    print(hash.encrypt(a))
    print(hash.encrypt(a, salt="cheney"))
    print(hash.encrypt(a, salt="cheney", _coding="GBK"))
