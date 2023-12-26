# -*- coding: utf-8 -*-
# @Time : 2022/5/9 01:05
# @Author : cheney
# @File : des2.py
# @Software: PyCharm
# @Site: www.cheney.cc

# -*- coding: utf-8 -*-
# @Time : 2022/4/10 21:33
# @Author : cheney
# @File : des.py
# @Software: PyCharm
# @Site: www.cheney.cc

import base64
import random

# IP置换表
_IP_table = [58, 50, 42, 34, 26, 18, 10, 2,
             60, 52, 44, 36, 28, 20, 12, 4,
             62, 54, 46, 38, 30, 22, 14, 6,
             64, 56, 48, 40, 32, 24, 16, 8,
             57, 49, 41, 33, 25, 17, 9, 1,
             59, 51, 43, 35, 27, 19, 11, 3,
             61, 53, 45, 37, 29, 21, 13, 5,
             63, 55, 47, 39, 31, 23, 15, 7
             ]
# 逆IP置换表
_IP_table_v = [40, 8, 48, 16, 56, 24, 64, 32,
               39, 7, 47, 15, 55, 23, 63, 31,
               38, 6, 46, 14, 54, 22, 62, 30,
               37, 5, 45, 13, 53, 21, 61, 29,
               36, 4, 44, 12, 52, 20, 60, 28,
               35, 3, 43, 11, 51, 19, 59, 27,
               34, 2, 42, 10, 50, 18, 58, 26,
               33, 1, 41, 9, 49, 17, 57, 25
               ]
# S盒中的S1盒
S1 = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
      0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
      4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
      15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13
      ]
# S盒中的S2盒
S2 = [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
      3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
      0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
      13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9
      ]
# S盒中的S3盒
S3 = [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
      13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
      13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
      1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12
      ]
# S盒中的S4盒
S4 = [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
      13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
      10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
      3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14
      ]
# S盒中的S5盒
S5 = [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
      14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
      4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
      11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3
      ]
# S盒中的S6盒
S6 = [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
      10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
      9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
      4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13
      ]
# S盒中的S7盒
S7 = [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
      13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
      1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
      6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12
      ]
# S盒中的S8盒
S8 = [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
      1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
      7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
      2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11
      ]
# S盒
_S = [S1, S2, S3, S4, S5, S6, S7, S8]
# P盒
_P_table = [16, 7, 20, 21,
            29, 12, 28, 17,
            1, 15, 23, 26,
            5, 18, 31, 10,
            2, 8, 24, 14,
            32, 27, 3, 9,
            19, 13, 30, 6,
            22, 11, 4, 25
            ]
# 压缩置换表1，不考虑每字节的第8位，将64位密钥减至56位。然后进行一次密钥置换。
_PC_1 = [57, 49, 41, 33, 25, 17, 9,
         1, 58, 50, 42, 34, 26, 18,
         10, 2, 59, 51, 43, 35, 27,
         19, 11, 3, 60, 52, 44, 36,
         63, 55, 47, 39, 31, 23, 15,
         7, 62, 54, 46, 38, 30, 22,
         14, 6, 61, 53, 45, 37, 29,
         21, 13, 5, 28, 20, 12, 4
         ]

# 压缩置换表2，用于将循环左移和右移后的56bit密钥压缩为48bit
_PC_2 = [14, 17, 11, 24, 1, 5,
         3, 28, 15, 6, 21, 10,
         23, 19, 12, 4, 26, 8,
         16, 7, 27, 20, 13, 2,
         41, 52, 31, 37, 47, 55,
         30, 40, 51, 45, 33, 48,
         44, 49, 39, 56, 34, 53,
         46, 42, 50, 36, 29, 32
         ]

# 用于对数据进行扩展置换，将32bit数据扩展为48bit
_E_extend = [32, 1, 2, 3, 4, 5,
             4, 5, 6, 7, 8, 9,
             8, 9, 10, 11, 12, 13,
             12, 13, 14, 15, 16, 17,
             16, 17, 18, 19, 20, 21,
             20, 21, 22, 23, 24, 25,
             24, 25, 26, 27, 28, 29,
             28, 29, 30, 31, 32, 1
             ]
# 每轮循环左移位数
_left_rotations = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


def __replace(source: list, table: list) -> list:
    """
    用table表对source做置换 得到 置换后的列表ans
    :param source: 要进行置换的列表(不会直接影响这个列表的内容)
    :param table: 里面储存的是置换的规则 如：PC1，IP
    :return: 新的 置换后的列表
    """
    ans = ["0" for t in range(len(table))]
    for i in range(len(table)):
        ans[i] = str(source[table[i] - 1])  # 注意统一用str 不是 int
    return ans


def __text_to_64bit(text: bytes) -> list:
    """
    将传入的text转换成若干个长度为64的由0/1组成的字符串(不足的补0) 并由列表的形式返回
    :param text: 要转换的文本
    :return: 返回的是一个列表(text_64_mat) 其中每个元素都是长为64的字符串
    """
    if type(text) != type(b'123'):  # 判断是否为字节(Byte)类型
        raise UnicodeDecodeError('解析到无法识别部分')
    else:
        text_en = text  # 是的话不做处理 (来自要解密的密文)

    text_64_mat = []  # 转换成的目标列表
    text_64 = ""  # 转换过程中用到的量 用来表示text_64_mat的一个元素
    cnt = 0  # 计数器
    for tex in text_en:
        cnt += 1
        text_8 = bin(int(str(tex), 10)).replace('0b', '').rjust(8, "0")
        text_64 += text_8
        if cnt % 8 == 0 and cnt >= 0:  # 八的倍数(>=1)
            text_64_mat.append(text_64)  # 加入一个64位的字符串
            text_64 = ""  # 在下一轮开始前 清空
        elif cnt == len(text_en):  # 不足64位 补0
            text_64_mat.append(text_64.ljust(64, "0"))
            # if self._is_debug >=2: print("此处补了", 64 - len(text_64), "个0")

    return text_64_mat


def __bit64_to_text(text_64_mat: list) -> bytes:
    """
    将二进制列表转化成可读的句子(解密的结果会用到)
    :param text_64_mat: 二进制列表
    :return:
    """
    # 每八个bit转一个八进制 然后将其转为byte类型
    word_list = []  # 储存bytes内的每个元素
    for text_64 in text_64_mat:
        for ii in range(8):
            if int(str(text_64[8 * ii:8 * (ii + 1)]), 2) == 0:
                break
            else:
                word_list.append((int(str(text_64[8 * ii:8 * (ii + 1)]), 2)))

    a = bytes(word_list)  # 转为byte类型
    # print(a.decode(encoding = "utf-8"))
    return a


def __get_key_48(key, _is_debug=0) -> list:
    """
    用来初始化key_48_mat,由输入的密钥生成每轮需要用的密钥
    :param _is_debug:
    :param key: 用户输入的密钥
    :return: 每轮需要用的密钥key_48_mat
    """
    if _is_debug: print("get key 48 ... ... ... ... ")
    # 先将字符串类型的密钥转换成二进制

    if type(key) == type(123) and 2 ** 64 > key > 2 ** 63:  # 判断是否为int 确保是64bit
        key_64 = str(bin(key))[2:]
    elif type(key) == type("123"):
        key_64 = __text_to_64bit(str(key).encode())[0]
    else:
        raise UnicodeDecodeError('密钥不是64位数据')

    '''做PC-1置换 生成Key_56 (去除8位校验位)'''
    key_56 = __replace(list(key_64), _PC_1)
    if _is_debug: print("Key_64:", key_64, "\nKey_56:", "".join(key_56))

    '''按照移位次数表做循环左移'''
    _key_48_mat = []
    for _round in range(16):
        num = _left_rotations[_round]  # 第 round 轮要移动的位数
        # 左右分别进行移位
        if num == 1:
            key_56 = key_56[1:28] + key_56[0:1] + key_56[29:57] + key_56[28:29]
        elif num == 2:
            key_56 = key_56[2:28] + key_56[0:2] + key_56[30:57] + key_56[28:30]
        else:
            raise ValueError('密钥左移位数出错 ！！！', _left_rotations[_round])

        '''做PC-2置换 生成Key_48'''
        key_48 = __replace(key_56, _PC_2)

        _key_48_mat.append(key_48)

    return _key_48_mat


def __round_fun(text_32: list, _round: int, _key_48_mat: list, _is_debug=0) -> list:
    """
    轮函数，对输入的32位数据 做当前轮对应的操作 E拓展/异或/S盒/P置换
    :param text_32: 输入的32位数据
    :param _round: 轮次
    :return: 最后处理完的32位数据
    """
    if _is_debug >= 2: print("\n>>>>轮数：", _round)
    '''E拓展 32->48'''
    text_48 = __replace(text_32, _E_extend)
    if _is_debug >= 2: print("\tE拓展之前", "".join(text_32));print("\tE拓展之后", "".join(text_48))

    '''异或'''
    text_48_xor = ["0" for t in range(48)]
    for i in range(48):
        if text_48[i] == _key_48_mat[_round][i]:
            text_48_xor[i] = "0"  # 相同为0
        else:
            text_48_xor[i] = "1"
    if _is_debug >= 2: print("\t对应的key_48", "".join(_key_48_mat[_round]));print("\txor之后  ",
                                                                                "".join(text_48_xor))

    '''S盒 '''
    text_32_s = []
    for box_num in range(8):  # 遍历8个S盒
        text_i_box_all = text_48_xor[6 * box_num:6 * box_num + 6]  # 填入第i个s盒
        if _is_debug >= 2: print("> box", box_num, text_i_box_all, "\t", end="");

        # 分离s盒内部的首尾 和中间四位
        text_i_box_side = [text_i_box_all[0], text_i_box_all[-1]]
        text_i_box_center = [text_i_box_all[t + 1] for t in range(4)]
        row = (int("".join(text_i_box_side), 2))  # 将二进制text_i_box_side转为十进制行数
        col = (int("".join(text_i_box_center), 2))  # 将text_i_box_center转为列数
        if _is_debug >= 2: print("row ", row, "  col", col, "\t", end="")

        # 找到s盒对应的位置
        data_t = _S[box_num][row * 16 + col]
        data_bin = bin(int(str(data_t), 10))  # 十进制转换成对应的二进制
        if _is_debug >= 2: print(data_t, "->", data_bin)

        for j in range(6 - len(data_bin)):
            text_32_s.append("0")
        for t in range(len(data_bin) - 2):
            text_32_s.append(str(data_bin[t + 2]))

    '''P置换  32 -> 32'''
    text_32_p = __replace(text_32_s, _P_table)
    if _is_debug >= 2: print("text_32_s", "".join(text_32_s));print("text_32_p", "".join(text_32_p))

    return text_32_p


def __main_frame(sourcetext_64: list, _key_48_mat: list, _is_debug: int = 0) -> str:
    """
    执行加/解密的主操作,包括：IP置换、16轮迭代(调用轮函数)、异或、前后颠倒、IP逆置换
    :param sourcetext_64: 源操作文本  targettext目标文本
    :return: 返回对原文本处理的结果 即targettext
    """
    if _is_debug: print("初始的64位文本", sourcetext_64)
    '''先IP置换 得到 plaintext_64 '''
    sourcetext_64_after_ip1 = __replace(sourcetext_64, _IP_table)

    if _is_debug: print("IP置换后：", "".join(sourcetext_64_after_ip1))

    '''再16轮迭代'''
    text_l = sourcetext_64_after_ip1[0:32]
    text_r = sourcetext_64_after_ip1[32:64]

    if _is_debug >= 2: print("text_l", text_l);print("text_r", text_r)

    for _round in range(16):
        tmp = text_r.copy()
        f_ = __round_fun(text_r, _round, _key_48_mat)  # 轮函数处理
        """异或***"""
        for n in range(32):
            if text_l[n] == f_[n]:
                text_r[n] = "0"  # 相同为0
            else:
                text_r[n] = "1"
        text_l = tmp.copy()

        if _is_debug >= 2: print("text_l", text_l);print("text_r", text_r)
        # print(round, "\t", tmp.extend(text_r))

    '''然后前后颠倒 形成经过十六轮代换之后的数据'''
    text_r.extend(text_l)  # 前后颠倒合并
    sourcetext_after_16round = text_r
    if _is_debug: print("十六轮代换之后", "".join(sourcetext_after_16round))

    '''最后IP逆置换 得到密文(二进制)'''
    targettext = __replace(sourcetext_after_16round, _IP_table_v)
    if _is_debug: print("IP逆置换后", "".join(targettext))

    # targettext是列表 需要用"".join将其转换位字符串
    return "".join(targettext)


def newkey() -> int:
    """
    获取一个64 bit的密钥
    :return: 返回密钥的十进制表示
    """
    return random.randint(2 ** 63, 2 ** 64)


def encrypt(plaintext: str, key) -> str:
    """
    加密函数,首先将明文转化为二进制矩阵，然后调用主循环实现加密，加密的结果转换为base64编码输出为密文
    :param key: 密钥(64位二进制的十进制表示)
    :param plaintext: 明文
    :return: 加密的结果(密文)
    """
    _key_48_mat = __get_key_48(key)
    secret_64_mat = []
    # if type(plaintext) != type(b'123'):  # 判断是否为字节(Byte)类型
    plaintext = str(plaintext).encode(encoding="utf-8")

    # 调用主循环实现加密
    for plaintext_64 in __text_to_64bit(plaintext):
        secret = __main_frame(plaintext_64, _key_48_mat)
        secret_64_mat.append(secret)

    return str(secret_64_mat)


def decrypt(secrettext: str, key) -> str:
    """
    DES的解密过程和DES的加密过程完全类似，只不过将16圈的子密钥序列K1，K2……K16的顺序倒过来
    首先将获得的密文用base64解码为字节码，再将其转化为二进制矩阵，然后调用主循环实现解密，再将得到的明文转化为可识别文本输出
    :param key: 密钥(64位二进制的十进制表示)
    :param secrettext: 密文(二进制经过base64编码过后的结果)
    :return: 可以直接识读的字符串明文
    """
    # secrettext = "b'" + secrettext + "'"  # 加上字节码的符号
    _key_48_mat = __get_key_48(key)
    _key_48_mat.reverse()  # 逆转密钥表 用于解密

    plain_text_mat = []
    if isinstance(eval(secrettext), int):
        secrettext=[secrettext]
    else:
        secrettext = eval(secrettext)
    for secrettext_64 in list(secrettext):
        plain = __main_frame(secrettext_64, _key_48_mat)  # 对每64位进行解密
        plain_text_mat.append(plain)  # 拼接每个部分解密的结果

    try:
        # 将得到的二进制明文转为可识别的文本，还原
        ans = __bit64_to_text(plain_text_mat).decode(encoding="utf-8")
    except UnicodeDecodeError:
        # ans = "解析出无法识别的明文，请检查密钥和明文！！！"
        raise UnicodeDecodeError('解析出无法识别的明文，请检查密钥和明文！！！')

    return ans
