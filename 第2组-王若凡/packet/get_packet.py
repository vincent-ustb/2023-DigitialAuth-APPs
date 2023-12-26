import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')
import datetime
import time
import rsa2
import hash
import dictionary
# from Packet import dictionary
import des2


class GetHeader:
    # 报文各字段，各字段设置为定长，位数不够则补0
    # 要直接调用
    # 传入的content需要为二进制字符串
    def __init__(self, pac_type, sign, control_type, src_id, dst_id, sessionkey=None, privatekey=None,
                 content='', state='none', ack='NO', code_type='utf-8'):
        '''
        :param pac_type: 报文的发送方与接收方类型，传入格式见dictionary，如'c_a'
        :param sign: 在上者基础上精确发送方与接收方类型
        :param control_type: 控制字段，根据上两个字段确定可以使用的功能
        :param src_id: 发送方地址
        :param dst_id: 接收方地址
        :param sessionkey: 用于DES加密的对称钥
        :param privatekey: 用于RSA加密摘要的私钥
        :param content: 数据字段，为二进制字符串
        :param state: 状态码，一般情况下默认为none
        :param ack: ack，用于双向不可否认，默认为‘NO’
        :param code_type: 编码类型，默认为‘utf-8’
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
        # length位数不知道够不够，先暂定16位
        # 若要修改，还要修改解析报文部分分片
        self.length = format(len(content), 'b').zfill(16)
        self.content = content
        self.privatekey = privatekey
        # self.x, self.privatekey = rsa2.newkeys(64)
        self.sessionkey = sessionkey

    # 4bit
    # 根据pac_type和sign两个字段判断对应的字典，来找到功能对应的二进制编码
    def get_control_type(self, control_type):
        if self.pac_type == '0001':
            self.get_control_type = dictionary.control_type1.get(control_type)
        elif self.pac_type == '0010':
            self.get_control_type = dictionary.control_type2.get(control_type)
        elif self.pac_type == '0011':
            self.get_control_type = dictionary.control_type3.get(control_type)
        elif self.pac_type == '0100':
            self.get_control_type = dictionary.control_type4.get(control_type)
        elif self.pac_type == '0101':
            if self.sign == '0001':
                self.get_control_type = dictionary.control_type5.get(control_type)
            elif self.sign == '0010':
                self.get_control_type = dictionary.control_type6.get(control_type)
            elif self.sign == '0011':
                self.get_control_type = dictionary.control_type7.get(control_type)
        elif self.pac_type == '0110':
            if self.sign == '0001':
                self.get_control_type = dictionary.control_type8.get(control_type)
            elif self.sign == '0010':
                self.get_control_type = dictionary.control_type9.get(control_type)
            elif self.sign == '0011':
                self.get_control_type = dictionary.control_type10.get(control_type)
        return self.get_control_type

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
    def __get_src_time(self):
        # 取整
        timestamp = int(time.time())
        ret_datetime = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        print(ret_datetime)
        self.src_time = format(timestamp, 'b').zfill(32)
        return self.src_time

    # 暂定16bit
    def get_length(self):
        self.length = format(len(self.content), 'b').zfill(16)
        return self.length

    def get_sec_packet(self) -> bytes:
        header = self.pac_type + self.sign + self.state \
                 + self.ack + self.code_type + GetHeader.get_control_type(self, self.control_type) \
                 + GetHeader.__get_src_id(self) + GetHeader.__get_dst_id(self) \
                 + GetHeader.__get_src_time(self) + self.length + self.content
        # 若不需要数字签名
        if not self.privatekey:
            # 若不需要DES加密，则不对报文做处理
            if self.sessionkey is None:
                # return header
                return bytes(header, encoding = 'utf8')
            # 若需要DES加密，则加密。返回一个str
            else:
                secret_packet = des2.encrypt(header, int(self.sessionkey))
                print(secret_packet)
                # return ''.join(eval(secret_packet))
                return bytes(secret_packet, encoding='utf8')
        # 若需要数字签名，则也一定需要DES加密
        else:
            # 摘要
            excerpt = hash.encrypt(header, salt="cheney")
            # 对摘要rsa加密
            secret_excerpt = rsa2.encrypt(excerpt, self.privatekey)
            # 加密后的摘要与原报文合并
            print(secret_excerpt)
            plain_packet = header + secret_excerpt
            print(plain_packet)
            # DES加密
            secret_packet = des2.encrypt(plain_packet, int(self.sessionkey))
            print(secret_packet)
            # return "".join(secret_packet)
            print('发出：', bytes(secret_packet, encoding='utf8'))
            return bytes(secret_packet, encoding='utf8')
            # return plain_packet


if __name__ == "__main__":
    # 最后两个字段分别是int(64位)和[int,int]
    A = GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55', des2.newkey(), [173359832571581378617429737117999267869035779672175511072753557771372548196663695653088634511986496906853490913647459933798961725280633495053233227703483939686501860019207625267354682981668162448576706509290699228246489919621363666240067854273996471648711595630886048538073504502721522298498589130569877087991, 9205368224805883662490737830090444362485992847691697491999670125949867521009348320380066956096754646014467375368008309346176767382953210595316411071732365205422848010103108734219181861508580828852148448744822724476152991974822149518433845051215969481496966520080173332505812012072096845427632326408063129473])
    # A = GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55', des2.newkey())
    # A = GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55')
    print(">>>", A.get_sec_packet())
    print(A.sessionkey)
    print(A.get_sec_packet())
    # print(A.x)
    # print(A.get_src_time())
    # print(A.get_sec_packet())
    # 要直接调用下面这个，需要先运行上面这个
    # print(A.get_src_id)
