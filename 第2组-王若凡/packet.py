"""
这是packet文件夹下的各个程序的再一次封装
为的是统一接口，简化调用
主要功能：
    1：打包函数，传入各个字段，返回bytes类型可发送报文
    2：解析类，需要先通过报文实例化对象，然后通过对象访问各个字段

注意：
    - 解析对象之前要先用check_sig验证数字签名
    - 注意数字签名和双向不可否认
    - Kerberos涉及到的六部都没有数字签名，所以前六步不做相应的处理（对应的参数可选），也不需要验证数字签名
    - 验证错误需要返回错误提示报文（包含错误代码）
    - 发送注册请求时的格式str([id,passwd]),解析注册请求eval(xxx),具体操作写在example.ipynb里面了

第五、六步要在content里面发送公钥和session key
之后的步骤才开始验证数字签名
所以前六步，关于密钥的字段都是空的

关于c-v双方的公钥什么时候生成和传输：
client的rsa密钥是由tgs生成的，第4步发给client，其中publicKey在证书内部。


"""

import re
import datetime
import time
import hash
import dictionary
import des2
import log
import rsa2


class GetHeader:
    length = ''
    total_length = ''

    # 报文各字段，各字段设置为定长，位数不够则补0
    # 可直接调用
    # 传入的content需要为二进制字符串
    def __init__(self, pac_type, sign, control_type, src_id, dst_id, piece='0', sessionkey=None, privatekey=None,
                 content='1', state='none', ack='NO', code_type='utf-8'):
        '''
        :param pac_type: 报文的发送方与接收方类型，传入格式见dictionary，如'c_a'
        :param sign: 在上者基础上精确发送方与接收方类型
        :param control_type: 控制字段，根据上两个字段确定可以使用的功能
        :param src_id: 发送方地址，不是IP
        :param dst_id: 接收方地址，不是IP
        :param sessionkey: 用于DES加密的对称钥
        :param privatekey: 用于RSA加密摘要的私钥
        :param content: 数据字段，为二进制字符串
        :param state: 状态码，一般情况下默认为none
        :param ack: ack，用于双向不可否认，默认为‘NO’
        :param code_type: 编码类型，默认为‘utf-8’
        :param piece: 2bit,判断是否需要分片
        '''
        if privatekey is None:
            privatekey = None
        self.pac_type = dictionary.pac_type.get(pac_type)
        self.sign = dictionary.sign.get(sign)
        self.state = dictionary.state.get(state)
        self.ack = dictionary.ack.get(ack)
        self.code_type = dictionary.code_type.get(code_type)
        self.control_type = control_type
        self.src_id = src_id
        self.dst_id = dst_id
        self.piece = piece.zfill(2)
        self.src_time = int(time.time())
        # length位数不知道够不够，先暂定16位
        # 若要修改，还要修改解析报文部分分片
        # self.length = format(len(content), 'b').zfill(24)
        # self.total_length = self.length.zfill(24)
        # self.length = length
        # self.total_length = length
        self.length = format(len(content), 'b').zfill(24)
        self.total_length = ''
        self.content = content
        self.privatekey = privatekey
        # self.x, self.privatekey = rsa2.newkeys(64)
        self.sessionkey = sessionkey

    # 4bit
    # 根据pac_type和sign两个字段判断对应的字典，来找到功能对应的二进制编码
    # 如果用不存在的键查找字典值，则输出KeyError
    def get_control_type(self, control_type):
        if self.pac_type == '0001':
            self.get_control_type = dictionary.control_type1.get(control_type, '字典键不存在')
        elif self.pac_type == '0010':
            self.get_control_type = dictionary.control_type2.get(control_type, '字典键不存在')
        elif self.pac_type == '0011':
            self.get_control_type = dictionary.control_type3.get(control_type, '字典键不存在')
        elif self.pac_type == '0100':
            self.get_control_type = dictionary.control_type4.get(control_type, '字典键不存在')
        elif self.pac_type == '0101':
            if self.sign == '0001':
                self.get_control_type = dictionary.control_type5.get(control_type, '字典键不存在')
            elif self.sign == '0010':
                self.get_control_type = dictionary.control_type6.get(control_type, '字典键不存在')
            elif self.sign == '0011':
                self.get_control_type = dictionary.control_type7.get(control_type, '字典键不存在')
            else:
                print("sign设置错误")
        elif self.pac_type == '0110':
            if self.sign == '0001':
                self.get_control_type = dictionary.control_type8.get(control_type, '字典键不存在')
            elif self.sign == '0010':
                self.get_control_type = dictionary.control_type9.get(control_type, '字典键不存在')
            elif self.sign == '0011':
                self.get_control_type = dictionary.control_type10.get(control_type, '字典键不存在')
            else:
                print("sign设置错误")
        if self.get_control_type == '字典键不存在':
            raise KeyError
        return self.get_control_type

    #   g
    # 要将二进制串转换为最初的样子，将二进制串每8位分隔开，分别转化为十进制然后中间用.隔开
    # 32bit
    def __get_src_id(self):
        # ip地址转换
        list1 = self.src_id.split('.')
        list2 = []
        for item in list1:
            item = bin(int(item))
            item = item[2:]  # 删去每段二进制串开头的0b
            list2.append(item.zfill(8))
        self.get_src_id = ''.join(list2)
        return self.get_src_id

    # 32bit
    def __get_dst_id(self):
        # ip地址转换
        list1 = self.dst_id.split('.')
        list2 = []
        for item in list1:
            item = bin(int(item))
            item = item[2:]  # 删去每段二进制串开头的0b
            list2.append(item.zfill(8))
        self.get_dst_id = ''.join(list2)
        return self.get_dst_id

    # 暂定32bit
    # 将获取时间戳，再将时间戳转成二进制
    def get_src_time(self):
        # 取整
        timestamp = int(time.time())
        # timestamp = self.src_time
        # ret_datetime = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        # print(ret_datetime)
        self.src_time = format(timestamp, 'b').zfill(32)
        return self.src_time

    # 暂定16bit
    def get_length(self):
        # 如果length长度大于65536，则报错
        if len(self.content) > 2 ** 24:
            # print("length位数不够：" + str(len(self.content)))
            raise ValueError
        length = format(len(self.content), 'b').zfill(24)
        return length

    def get_header(self):
        header = self.pac_type + self.sign + self.state \
                 + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                 + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                 + GetHeader.get_src_time(self) + self.length + self.total_length
        return header

    def get_sec_packet(self) -> bytes:

        # header = self.pac_type + self.sign + self.state \
        #         + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
        #         + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
        #         + GetHeader.__get_src_time(self) + GetHeader.get_length(self) + self.content
        # 现在的length为des加密后的content长度
        header = self.pac_type + self.sign + self.state \
                 + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                 + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                 + GetHeader.get_src_time(self) + self.length + self.total_length
        # 除开报文的总长度

        # 若不需要数字签名
        if not self.privatekey:
            # 若不需要DES加密，则不对报文做处理
            if self.sessionkey is None:
                # return header
                log_txt = ""
                log_txt += "未加密的content内容为：" + str(self.content) + "\n"
                log.debug(log_txt, path="./log/", log_name="get_packet.txt")
                self.length = format(len(self.content), 'b').zfill(24)
                self.total_length = self.length
                # header = self.pac_type + self.sign + self.state \
                #         + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                #         + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                #        + GetHeader.__get_src_time(self) + format(len(self.content), 'b').zfill(24) + \
                #         format(len(self.content), 'b').zfill(24)
                header = self.pac_type + self.sign + self.state \
                         + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                         + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                         + GetHeader.get_src_time(self) + GetHeader.get_length(self) + format(len(self.content),
                                                                                              'b').zfill(24)
                packet = header + str(self.content)
                return bytes(packet, encoding='utf8')
            # 若需要DES加密，则加密。返回一个str
            else:
                len_content = len(des2.encrypt(self.content, int(self.sessionkey)))
                # print("加密后的content长度为：", len_content)
                self.length = format(len_content, 'b').zfill(24)
                # print(format(len_content, 'b').zfill(24))
                self.total_length = self.length
                header = self.pac_type + self.sign + self.state \
                         + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                         + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                         + GetHeader.get_src_time(self) + GetHeader.get_length(self) + format(len_content,
                                                                                              'b').zfill(24)
                secret_packet = header + des2.encrypt(self.content, int(self.sessionkey))

                # print(secret_packet)
                # return ''.join(eval(secret_packet))
                log_txt = ""
                log_txt += "未加密的content内容为：" + str(self.content) + "\n"
                log_txt += "DES加密后的无数字签名的数据字段内容为：" + secret_packet + "\n" + "类型为：" + str(type(secret_packet)) + "\n"
                log.debug(log_txt, path="./log/", log_name="get_packet.txt")
                return bytes(secret_packet, encoding='utf8')
        # 若需要数字签名，则也一定需要DES加密
        else:
            # 摘要
            excerpt = hash.encrypt(self.content, salt="1")
            # print("rsa加密前的摘要长度", len(excerpt))
            # 对摘要rsa加密
            # print(excerpt)
            secret_excerpt = rsa2.encrypt(excerpt, self.privatekey)
            # print("rsa加密后的摘要长度", len(secret_excerpt))
            # print("content长度为", len(self.content))
            # 加密后的摘要与原报文数据字段合并
            # print(secret_excerpt)
            plain_packet = self.content + secret_excerpt

            # print("DES加密前长度为：", len(plain_packet))
            # DES加密 对原数据字段和数字签名加密
            secret_content = des2.encrypt(self.content, int(self.sessionkey))
            self.length = format(len(secret_content), 'b').zfill(24)
            # print("长度为：", len(secret_content), '加密前长度：', len(self.content))
            # total = secret_content + des2.encrypt(secret_excerpt, int(self.sessionkey))
            total = des2.encrypt(plain_packet, int(self.sessionkey))
            # print("DES加密后：", len(total))
            # print(type(total), total)
            self.total_length = format(len(total), 'b').zfill(24)

            sec_total = des2.encrypt(plain_packet, int(self.sessionkey))
            # print("总长度为：", self.total_length)
            header = self.pac_type + self.sign + self.state \
                     + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                     + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) + self.piece \
                     + GetHeader.get_src_time(self) + GetHeader.get_length(self) + format(len(total), 'b').zfill(24)
            secret_packet = header + total
            # print(secret_packet)
            # return "".join(secret_packet)
            # print('发出：', bytes(secret_packet, encoding='utf8'))
            log_txt = ""
            log_txt += "未加密的content内容为：" + str(self.content) + "\n"
            log_txt += "对content摘要私钥rsa加密后的数字签名为：" + secret_excerpt + "\n" + "类型为：" + str(
                type(secret_excerpt)) + "\n"
            log_txt += "DES加密后的有数字签名的报文内容为：" + secret_packet + "\n" + "类型为：" + str(type(secret_packet)) + "\n"\
                       + "DES加密后的数据字段长度为" + str(int(self.length, 2)) + "\n "
            log.debug(log_txt, path="./log/", log_name="get_packet.txt")
            # print("输出的报文为：", secret_packet)
            return bytes(secret_packet, encoding='utf8')
            # return plain_packet


# def get_pack(pac_type, sign, control_type, src_id, dst_id, private_key=-1, session_key: int = -1,
#              content: str = '', state='none', ack: bool = False, code_type='utf-8') -> bytes:
def get_pack(pac_type, sign="none", control_type="unknown1", src_id="127.0.0.1", dst_id="127.0.0.1", piece='0',
             sessionkey=None,
             privatekey=None,
             content='1', state='none', ack='NO', code_type='utf-8') -> bytes:
    """
    打包报文的函数: 传入要打包的各个字段（注意顺序），有些是有默认值的，
    :param pac_type: 数据包的类型 比如c_a,v_c
    :param sign: 在上者基础上精确发送方与接收方类型,与KDC交互时不需要
    :param control_type: 控制字段的含义要取决于数据包的类型，比如pac_type为c_a ,control_type为"request_enroll",含义为client向as请求注册。
    :param src_id: 发送方地址，不是ip
    :param dst_id: 接收方地址，不是ip
    :param privatekey: 自己的私钥，用于数字签名
    :param sessionkey: 会话密钥(des) 用于加密，实际是64 bit的密钥的十进制表示
    :param content: 数据字段，传入str类型（实际使用可用dict等转为str）默认为空
    :param state: 状态码，一般情况下默认为none
    :param ack: 用于双向不可否认，默认为‘NO’
    :param code_type: 编码类型(默认utf-8)
    :return: 返回一个能够在socket传输，并且结果数字签名，和session key加密之后的报文
    """
    # 当pac_type为'c_s'or's_c'时，sign不能为默认参数，因为需具体到是哪类客户端
    # 各字段类型检查
    if pac_type not in dictionary.pac_type.keys():
        raise ValueError
    if sign not in dictionary.sign.keys():
        raise ValueError
    if state not in dictionary.state.keys():
        raise ValueError
    if ack not in dictionary.ack.keys():
        print(ack)
        raise ValueError
    if code_type not in dictionary.code_type.keys():
        raise ValueError

    if type(content) != type(""):
        print("content格式错误，应转为str")
        raise ValueError
    '''if type(sessionkey) != type(1):
        raise ValueError'''

    if type(privatekey) == type(""):
        privatekey = list(eval(privatekey))
    elif type(privatekey) == type(list([1, 2])):
        pass  # list不处理
    elif type(privatekey) == type(None):
        pass  # none不处理
    else:
        raise ValueError('rsa密钥类型出错' + str(type(privatekey)))

    obj = GetHeader(pac_type, sign, control_type, src_id, dst_id, piece, sessionkey, privatekey,
                    content, state, ack, code_type)
    # log.debug(content=content)
    return obj.get_sec_packet()


class pack:
    def __init__(self, sec_packet, sessionkey=None, publickey=None):
        '''
        :param sec_packet: 接收到的加密后的报文
        :param publickey: 发送方公钥，用于解密加密后的摘要 [int,int]型
        :param sessionkey: 用于des解密的对称钥，64bit的int型
        '''
        if type(sec_packet) != type(b''):
            raise ValueError
        # if type(sessionkey) != type(1):
        #    raise ValueError
        if type(publickey) == type(""):
            publickey = list(eval(publickey))
        elif type(publickey) == type(list([1, 2])):
            pass  # list不处理
        elif type(publickey) == type(None):
            pass  # none不处理
        else:
            raise ValueError('rsa密钥类型出错' + type(publickey))
        # self.length为des加密后的content长度；self.re_length为原始content长度
        self.sec_packet = sec_packet
        self.header = sec_packet[:168]
        self.length = int(self.header[120:144], 2)
        self.total_length = int(self.header[144:168], 2)
        # 若报文未用到sessionkey加密则不需要解密
        if not sessionkey:
            self.plain_packet = str(sec_packet, encoding='utf8')
            self.re_length = self.length
        # 反之，进行解密
        else:
            if not publickey:
                self.sec_content1 = str(sec_packet[168:], encoding='utf8')
                self.re_length = len(des2.decrypt(self.sec_content1, sessionkey))
                self.sec_content = ''.join(eval(self.sec_content1))
                self.plain_packet = str(self.header, encoding='utf8') + des2.decrypt(self.sec_content1,
                                                                                     sessionkey)
            # self.plain_packet = des2.decrypt(re.findall(r'.{64}', self.sec_packet), sessionkey)
            # self.sec_packet = sec_packet
            # self.header = sec_packet[:144]
            # self.length = int(self.header[120:144], 2)
            # print(self.length)
            # 分别DES加密后的数据字段与数字签名
            # 现在分别进行DES解密 先划分出加密后的content
            else:
                self.sec_packet1 = str(sec_packet[168:], encoding='utf8')
                # self.sec_content1 = str(sec_packet[168:168 + self.length], encoding='utf8')
                # 为des解密后的content长度，即content实际长度
                # self.re_length = len(des2.decrypt(self.sec_content1, sessionkey))
                # print(self.re_length)
                # self.sec_excerpt1 = str(sec_packet[168 + self.length:], encoding='utf8')
                # print(self.sec_content + self.sec_excerpt)
                self.sec_packet = ''.join(eval(self.sec_packet1))
                # self.sec_content = ''.join(eval(self.sec_content1))
                # self.sec_excerpt = ''.join(eval(self.sec_excerpt1))
                self.plain_packet = str(self.header, encoding='utf8') + des2.decrypt(self.sec_packet1, sessionkey)
                # self.plain_packet = str(self.header, encoding='utf8') + des2.decrypt(self.sec_content1, sessionkey)
                # + des2.decrypt(self.sec_excerpt1, sessionkey)
            # print("sec_packet为：", ''.join(eval(self.sec_packet1)))

        # print('收到：', self.plain_packet)
        # 报头部分
        self.header = self.plain_packet[:168]
        # 无字典部分转成十进制
        self.pac_type = int(self.header[0:4], 2)
        self.sign = int(self.header[4:8], 2)
        self.state = int(self.header[8:12], 2)
        # print(type(self.state), self.state)
        self.ack = int(self.header[12:14], 2)
        self.code_type = int(self.header[14:18], 2)
        # 暂定不需要根据值找对应的键
        # 根据pac_type和sign可以确定对应的字典，字典值对应不同的功能
        self.control_type = int(self.header[18:22], 2)
        self.src_id = self.header[22:54]
        self.dst_id = self.header[54:86]
        self.piece = int(self.header[86:88])
        self.src_time = self.header[88:120]
        self.length = int(self.header[120:144], 2)

        # 数据字段
        self.content = self.plain_packet[168:168 + self.length]
        self.publickey = publickey
        self.sessionkey = sessionkey
        self.dst_time = now_time = datetime.datetime.utcfromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M:%S")
        # 数字签名
        # self.len_secret_excerpt = len(sec_packet) - self.length - 1
        log_txt1 = ""
        log_txt1 += "DES解密后的报文为：" + self.plain_packet + "\n"
        log_txt1 += "数据字段的内容为：" + self.content + "\n"
        log.debug(log_txt1, path="./log/", log_name="parse_packet.txt")

    # 需要验证数字签名则调用
    def check_sig(self):
        # rsa加密后的摘要
        # secret_excerpt = self.plain_packet[144 + self.length:]
        secret_excerpt = self.plain_packet[168 + self.length:]
        # print("数字签名长度为：", len(secret_excerpt))
        excerpt = rsa2.decrypt(secret_excerpt, self.publickey)
        # 获取收到的报文摘要
        raw_excerpt = hash.encrypt(self.content, salt="1")
        # 将数字签名与报文摘要进行对比
        if raw_excerpt == excerpt:
            return 1
        else:
            # 发一个state为error的报文给发送方
            print("数字签名与摘要不匹配，返回一个状态码为error的报文给发送方")
            return 0

    def get_src_id(self):
        # 测试成功
        list1 = re.findall(r'.{8}', self.src_id)
        # list1 = re.findall(r'.{8}', src_id)
        list2 = []
        for n in list1:
            list2.append(str(int(n, 2)))
        src_id = ".".join(list2)
        # src_id = ".".join(list2)
        # print(src_id)
        # return src_id
        return src_id

    def get_dst_id(self):
        list1 = re.findall(r'.{8}', self.dst_id)
        list2 = []
        for n in list1:
            list2.append(str(int(n, 2)))
        dst_id = ".".join(list2)
        return dst_id

    def get_src_time(self):
        # 比较接收到的src_time与现在的时间，来判断是否是消息重放
        # 若秒数差值大于60，则判断可能消息重放
        timestamp = int(self.src_time, 2)
        timenow = int(time.time())
        src_time = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        now_time = datetime.datetime.utcfromtimestamp(timenow).strftime("%Y-%m-%d %H:%M:%S")
        src_datetime = datetime.datetime.strptime(src_time, "%Y-%m-%d %H:%M:%S")
        now_datetime = datetime.datetime.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        if (now_datetime - src_datetime).seconds > 60:
            print("有消息重放嫌疑")
            print("当前时间为：", now_datetime)
            print("报文发送时间为：", src_datetime)
        else:
            print("不存在消息重放")
        # print("时间差为：", (now_datetime - src_datetime).seconds)
        return src_time

    def __str__(self):
        print("*" * 70)
        num = 30
        char_ = "_"
        print("pac_type为：".ljust(num, char_), self.pac_type)
        print("sign为：".ljust(num, char_), self.sign)
        print("state为：".ljust(num, char_), self.state)
        print("ack为：".ljust(num, char_), self.ack)
        print("code_type为：".ljust(num, char_), self.code_type)
        print("control_type为：".ljust(num, char_), self.control_type)
        print("src_id为：".ljust(num, char_), self.get_src_id())
        print("dst_id为：".ljust(num, char_), self.get_dst_id())
        print("src_time为：".ljust(num, char_), self.get_src_time())
        print("length为：".ljust(num, char_), self.length)
        print("total_length为：".ljust(num, char_), self.total_length)
        return str("*" * 70)


def get_dict_key(value):
    key = list(dictionary.pac_type.keys())[list(dictionary.pac_type.values()).index(value)]
    return key


if __name__ == "__main__":
    # print(get_dict_key(format(3, 'b').zfill(4)))
    # print(format(0, 'b').zfill(2))
    publicKey, privateKey = rsa2.newkeys(512)
    # publicKey = rsa2.newkeys(128)[0]
    # privateKey = rsa2.newkeys(128)[1]
    # print(privateKey)
    # print(publicKey)
    sessionKey = des2.newkey()
    '''
    myPack2 = get_pack('a_c', content='364623543635gdf', sessionkey=sessionKey)
    # print((type(myPack2)), myPack2)
    print(myPack2.)
    pack_ans2 = pack(myPack2, sessionkey=sessionKey)
    # print(pack_ans2.check_sig())
    print(pack_ans2.get_src_time())
    print(pack_ans2.piece)
    print(pack_ans2.get_src_id())
    print(type(pack_ans2.content), pack_ans2.content)
    '''
    # 获得打包报文时的length与total_length示例
    # A = GetHeader('c_s', 'business', 'unknown2', '127.0.0.1', '127.0.0.1',
    # sessionkey=sessionKey, privatekey=privateKey, content='3futu325fcn' * 9)
    A = GetHeader('c_a', 'none', 'unknown1', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
                  privatekey=privateKey, content='3futu325fcn')
    # P = pack(A.get_sec_packet(), sessionKey, publicKey)
    P = pack(A.get_sec_packet(), sessionkey=sessionKey,
             publickey=publicKey)
    # print(P)
    # test_tkinter.send_show('c_s', 'business', 'unknown2', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
    #                        privatekey=privateKey,
    #                        content='3futu325fcn' * 9)
    # test_tkinter.send_show('c_s', 'business', 'unknown2', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
    #                        privatekey=privateKey,
    #                        content='3futu325fcn' * 20)
    # test_tkinter.recv_show(P)
    # test_tkinter.window.mainloop()
    # x = input(" ")
    # P = pack(A.get_sec_packet(), sessionKey)
    print("发送时间为：", P.get_src_time())
    print("数据字段长度为：", int(A.get_sec_packet()[120:144], 2))
    # print(int(A.get_length(), 2))
    # print(A.length)
    # print("发出的除开报头的总长度（total_length）为：", int(A.get_sec_packet()[144:168], 2))

    # print(A.get_sec_packet())
    # A =Ge tHeader('c_a', 'none', 'unknown1', '127.0.0.1', '127.0.0.1', content='3futu325fcn')
    # A = GetHeader('c_a', 'none', 'unknown1', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
    #               content='3futu325fcnhellonodia0284', )
    print(type(A.pac_type))
    print(type(A.sign))
    print(A.piece)
    # print("发出的除开报头的总长度为：", int(A.get_sec_packet()[144:168], 2))
    # print("发出的除开报头的总长度为：", int(A.total_length, 2))

    # P = pack(A.get_sec_packet())
    print("接收到的数据字段长度为：", P.length)
    print("接收的除开报头的总长度（total_length）为：", P.total_length)
    # print("接收到的除开报头的总长度为：", P.total_length)
    print("数字签名验证：", P.check_sig())
    print(P.state)
    print("接收时间为：", P.dst_time)
    # print(A.content)
    # print(A.control_type)
    re_time = int(A.src_time, 2)
    print(datetime.datetime.utcfromtimestamp(re_time).strftime("%Y-%m-%d %H:%M:%S"))
    # print(P.header)
    print((type(P.control_type), P.control_type))
    print(P.content)
    # print(P.sec_packet)
    print(P.get_src_time())
    print(P.get_src_id())
