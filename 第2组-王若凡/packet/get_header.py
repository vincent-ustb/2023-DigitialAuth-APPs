import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')
import hashlib
import time
import rsa2
import hash
import dictionary
# from Packet import dictionary
import des2


class GetHeader:
    # 报文各字段
    # 报头暂定共134bit
    '''
    def __init__(self, pac_type, sign, state, ack, code_type, control_type, src_id, dst_id):
        self.pac_type = pac_type
        self.sign = sign
        self.state = state
        self.ack = ack
        self.code_type = code_type
        self.control_type = control_type
        self.src_id = src_id
        self.dst_id = dst_id
    '''

    # 4bit
    def get_pac_type(self, pac_type):
        self.get_pac_type = dictionary.pac_type.get(pac_type)
        return self.get_pac_type
        # return int(self.get_pac_type, 10)

    # 4bit
    def get_sign(self, sign):
        self.get_sign = dictionary.sign.get(sign)
        return self.get_sign

    # 4bit
    def get_state(self, state):
        self.get_state = dictionary.state.get(state)
        return self.get_state

    # 2bit
    def get_ack(self, ack):
        self.get_ack = dictionary.ack.get(ack)
        return self.get_ack

    # 4bit
    def get_code_type(self, code_type):
        self.get_code_type = dictionary.code_type.get(code_type)
        return self.get_code_type

    # 4bit
    def get_control_type(self, control_type):
        if self.get_pac_type == '0001':
            self.get_control_type = dictionary.control_type1.get(control_type)
        elif self.get_pac_type == '0010':
            self.get_control_type = dictionary.control_type2.get(control_type)
        elif self.get_pac_type == '0011':
            self.get_control_type = dictionary.control_type3.get(control_type)
        elif self.get_pac_type == '0100':
            self.get_control_type = dictionary.control_type4.get(control_type)
        elif self.get_pac_type == '0101':
            if self.get_sign == '0001':
                self.get_control_type = dictionary.control_type5.get(control_type)
            elif self.get_sign == '0010':
                self.get_control_type = dictionary.control_type6.get(control_type)
            elif self.get_sign == '0011':
                self.get_control_type = dictionary.control_type7.get(control_type)
        elif self.get_pac_type == '0110':
            if self.get_sign == '0001':
                self.get_control_type = dictionary.control_type8.get(control_type)
            elif self.get_sign == '0010':
                self.get_control_type = dictionary.control_type9.get(control_type)
            elif self.get_sign == '0011':
                self.get_control_type = dictionary.control_type10.get(control_type)
        return self.get_control_type

    # 要将二进制串转换为最初的样子，将二进制串每8位分隔开，分别转化为十进制然后中间用.隔开
    # 32bit
    def get_src_id(self, src_id):
        # ip地址转换
        list1 = src_id.split('.')
        list2 = []
        for item in list1:
            item = bin(int(item))
            item = item[2:]  # 删去每段二进制串开头的0b
            list2.append(item.zfill(8))
        self.get_src_id = ''.join(list2)
        return self.get_src_id

    # 32bit
    def get_dst_id(self, dst_id):
        # ip地址转换
        list1 = dst_id.split('.')
        list2 = []
        for item in list1:
            item = bin(int(item))
            item = item[2:]  # 删去每段二进制串开头的0b
            list2.append(item.zfill(8))
        self.get_dst_id = ''.join(list2)
        return self.get_dst_id

    # 暂定32bit
    def get_src_time(self):
        # 取整
        timestamp = int(time.time())
        self.src_time = format(timestamp, 'b').zfill(32)
        return self.src_time

    # 暂定16bit
    def get_length(self, content):
        self.length = format(len(content), 'b').zfill(16)
        return self.length

    def get_header(self, pac_type, sign, control_type, src_id, dst_id, content='', state='none', ack='NO',
                   code_type='utf-8'):
        self.header = GetHeader.get_pac_type(self, pac_type) + GetHeader.get_sign(self, sign) + GetHeader.get_state(
            self, state) \
                      + GetHeader.get_ack(self, ack) + GetHeader.get_code_type(self,
                                                                               code_type) + GetHeader.get_control_type(
            self, control_type) \
                      + GetHeader.get_src_id(self, src_id) + GetHeader.get_dst_id(self,
                                                                                  dst_id) + GetHeader.get_src_time(self) \
                      + GetHeader.get_length(self, content) + content

        return self.header
        # 将报头与报文内容合并，报文内容结尾加'\r\n'作为结束符
        # packet = header +
        # return ''.join(format(ord(c), 'b') for c in '\r\n')

    # def get_packet(self):
    '''
    def get_hash(self, pwd, salt):
        
        :param pwd:
        :param salt:
        :return: hash_value
        
        hash = hashlib.sha256(str(salt).encode('utf8'))  # 同一种hash算法得到的长度是固定的
        hash.update(str(pwd).encode('utf8'))  # 如果pwd很大，可以持续读入，而不需要一次性读完
        hash_value = hash.hexdigest()
        return hash_value
    '''
'''
    # 直接得到加密后的报文
    def get_sec_packet(self, pac_type, sign, control_type, src_id, dst_id, privatekey, sessionkey, content='',
                       state='none', ack='NO', code_type='utf-8'):
        self.header = GetHeader.get_pac_type(self, pac_type) + GetHeader.get_sign(self, sign) + GetHeader.get_state(
            self, state) \
                      + GetHeader.get_ack(self, ack) + GetHeader.get_code_type(self,
                                                                               code_type) + GetHeader.get_control_type(
            self, control_type) \
                      + GetHeader.get_src_id(self, src_id) + GetHeader.get_dst_id(self,
                                                                                  dst_id) + GetHeader.get_src_time(self) \
                      + GetHeader.get_length(self, content) + content
        self.excerpt = hash.encrypt(GetHeader.get_header(), salt="cheney")
        secret_excerpt = rsa.encrypt(self.excerpt, privatekey)
        plain_packet = self.header + secret_excerpt
        secret_packet = des.encrypt(plain_packet, int(sessionkey))
        return secret_packet


'''
# 要加密整个报文，后续要将报文内容转换为二进制之后用hash加密
def get_sig(self, privatekey):
    """
    packet = self.header
    self.excerpt = hashlib.sha256(packet.salt)
    """
    self.excerpt = hash.encrypt(GetHeader.get_header(), salt="cheney")
    secret_excerpt = rsa2.encrypt(self.excerpt, privatekey)
    return secret_excerpt

    def get_sec_packet(self, privatekey, sessionkey):
        plain_packet = self.header + GetHeader.get_sig(self, privatekey)
        secret_packet = des2.encrypt(plain_packet, int(sessionkey))
        return secret_packet
    # 将sig与整个报文合并，然后调用DES加密，通过socket发送给接收方


if __name__ == "__main__":
    # h = GetHeader('c_s', 'user', 'success', 'NO', 'utf-8', 'modify', '204.148.21.114', '172.27.124.55')
    h = GetHeader()
    # 各字段分开运行
    print(h.get_pac_type('c_s'))
    # print (int(__get_pac_type(self, 't_c'), 2))
    print(h.get_sign('user'))
    print(h.get_state('success'))
    print(h.get_ack('NO'))
    print(h.get_code_type('utf-8'))
    # 单独运行前需先得到type和sign
    print(h.get_control_type('modify'))
    print(h.get_src_id('204.148.21.114'))
    print(h.get_dst_id('172.27.124.55'))
    print(h.get_src_time())
    # print(h.get_length())
    # 直接得到整个报文
    print(h.get_header('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55'))
    print(h.get_sig())
