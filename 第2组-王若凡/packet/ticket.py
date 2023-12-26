from datetime import datetime
from random import *


class GetCertificate:
    def __init__(self, user_id, pub_key, end_time='2100-5-11 11:41:34', version='v3'):
        '''
        :param version:
        :param serial_num:
        :param user_id:
        :param src_time:
        :param end_time:
        :param pub_key:
        :return: get_certificate
        '''
        self.version = ''.join(format(c, 'b') for c in bytearray(version, "utf-8"))
        self.serial_num = "".join([choice("0123456789ABCDEF") for i in range(16)])
        self.user_id = user_id
        self.src_time = datetime.now()
        self.end_time = end_time
        # self.pub_key = "".join([choice("01") for i in range(512)])
        self.pub_key = pub_key

if __name__ == "__main__":
    G = GetCertificate('204.148.21.114', 5342636316)
    print(G.serial_num)
    # get_pub_key = "".join([choice("01") for i in range(512)])
    print(G.version)
    print(G.src_time)

'''
g = GetCertificate()
    
    def get_ticket(src, dst, key, ad, publish_time, expire_time):
    :param src:
    :param dst:
    :param key:
    :param ad:
    :param publish_time:
    :param expire_time:
    :return:
    
    src = ''  # 发送方标识
    dst = ''  # 接收方标识
    key = ''
    ad = ''
    pubilish_time = datetime.now()
    expire_time = datetime()
    ticket = ''
    return ticket
'''
