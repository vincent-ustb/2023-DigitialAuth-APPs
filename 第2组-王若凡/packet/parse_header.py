import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')
# from Packet import dictionary
import dictionary
import des2
import rsa2
import re
import datetime
import hash
import get_packet


class ParseHeader:
    def __init__(self, sec_packet, sessionkey=None, publickey=None):
        '''
        :param sec_packet: 接收到的加密后的报文
        :param publickey: 发送方公钥，用于解密加密后的摘要 [int,int]型
        :param sessionkey: 用于des解密的对称钥，64bit的int型
        '''
        # 若报文未用到sessionkey加密则不需要解密

        if not sessionkey:
            self.plain_packet = str(sec_packet, encoding='utf8')
        # 反之，进行解密
        else:
            # self.plain_packet = des2.decrypt(re.findall(r'.{64}', self.sec_packet), sessionkey)
            self.sec_packet1 = str(sec_packet, encoding='utf8')
            # print(''.join(eval(self.sec_packet1)))
            self.sec_packet = ''.join(eval(self.sec_packet1))
            self.plain_packet = des2.decrypt(self.sec_packet1, sessionkey)
        print('收到：', self.plain_packet)
        # 报头部分
        self.header = self.plain_packet[:134]
        # 无字典部分转成十进制
        self.pac_type = int(self.header[0:4], 2)
        self.sign = int(self.header[4:8], 2)
        self.state = int(self.header[8:12], 2)
        self.ack = int(self.header[12:14], 2)
        self.code_type = int(self.header[14:18], 2)
        # 暂定不需要根据值找对应的键
        # 根据pac_type和sign可以确定对应的字典，字典值对应不同的功能
        self.control_type = int(self.header[18:22], 2)
        self.src_id = self.header[22:54]
        self.dst_id = self.header[54:86]
        self.src_time = self.header[86:118]
        self.length = int(self.header[118:134], 2)
        # 数据字段
        self.content = self.plain_packet[134:134 + self.length]
        self.publickey = publickey
        self.sessionkey = sessionkey

    # 需要验证数字签名则调用
    def check_sig(self):
        # rsa加密后的摘要
        secret_excerpt = self.plain_packet[134 + self.length:]
        print(secret_excerpt)
        excerpt = rsa2.decrypt(secret_excerpt, self.publickey)
        # 获取收到的报文摘要
        raw_excerpt = hash.encrypt(self.plain_packet[0:134 + self.length], salt="cheney")
        # 将数字签名与报文摘要进行对比
        if raw_excerpt == excerpt:
            return 1
        else:
            # 发一个state为error的报文给发送方
            return 0

    def get_src_id(self):
        # 测试成功
        list1 = re.findall(r'.{8}', self.src_id)
        # list1 = re.findall(r'.{8}', src_id)
        list2 = []
        for n in list1:
            list2.append(str(int(n, 2)))
        self.src_id = ".".join(list2)
        # src_id = ".".join(list2)
        # print(src_id)
        # return src_id
        return self.src_id

    def get_dst_id(self):
        list1 = re.findall(r'.{8}', self.dst_id)
        list2 = []
        for n in list1:
            list2.append(str(int(n, 2)))
        self.dst_id = ".".join(list2)
        return self.dst_id

    def get_src_time(self):
        timestamp = int(self.src_time, 2)
        ret_datetime = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return ret_datetime


if __name__ == "__main__":
    # P = ParseHeader(
    #    '00100100011000001001100000001110001001010010111001101001000111001101101111010000101110101010110100100101111110000001100001110001001010001101000010010001101001011001000010010111110010001011111010111100000011001011011111110110001001001100001100100110101011101101101100001010011010000111011110100101110100100100100110110011111111010110000000010000000000000010000011111101101000110010001010110000101000100011000100010011001110111100110000010110100010001000001110011011100001001010010110111110111011100111000101010001110000101010010110010010101100001111110110011101111101110000000100000010011011010000011001110010011111001110111101000000010000110101001111011001000011111100110111110010111110100101110000000000111101101010111100011000001111100100010111110100101010101011000111000011000100010001001000110110111110000010010110010001110111000101100000100111101111011111010010100010100010001111111100010011111100000110101000101001001101000100111100000110010111000011000011111000100000010100010001010101000010100110100100111100010001100000101111111101101010001111011010101000101000110011010001011100'
    #   17059515186458372621)
    # A = get_packet.GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55', des2.newkey())
    # A = get_packet.GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55')
    A = get_packet.GetHeader('c_s', 'user', 'modify', '204.148.21.114', '172.27.124.55', des2.newkey(),  [173359832571581378617429737117999267869035779672175511072753557771372548196663695653088634511986496906853490913647459933798961725280633495053233227703483939686501860019207625267354682981668162448576706509290699228246489919621363666240067854273996471648711595630886048538073504502721522298498589130569877087991, 9205368224805883662490737830090444362485992847691697491999670125949867521009348320380066956096754646014467375368008309346176767382953210595316411071732365205422848010103108734219181861508580828852148448744822724476152991974822149518433845051215969481496966520080173332505812012072096845427632326408063129473])
    P = ParseHeader(A.get_sec_packet(), A.sessionkey, [173359832571581378617429737117999267869035779672175511072753557771372548196663695653088634511986496906853490913647459933798961725280633495053233227703483939686501860019207625267354682981668162448576706509290699228246489919621363666240067854273996471648711595630886048538073504502721522298498589130569877087991, 65537])
    print(P.check_sig())
    print(A.control_type)
    print(P.header)
    print(P.pac_type)
    print(P.sign)
    print(P.get_src_time())
    print(P.get_src_id())

