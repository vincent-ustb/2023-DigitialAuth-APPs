# -*- coding: utf-8 -*-
# @Time : 2022/4/25 23:47
# @Author : cheney
# @File : tgs.py
# @Software: PyCharm
# @Site: www.cheney.cc

"""
tgs只干一件事：分发ticket
收取as的tgt，验证后回复一个ticket
"""

import redis
import socket
import threading
import config  # 读取公共的配置信息 只需修改一处即可。
import des2
import rsa2
import log
import hash
import mysocket

from packet import get_pack  # 用来打包
from packet import pack  # 用来解析报文

log_txt = ''
# 下面是全局的k_tgs以及hash后的k_tgs_hash,运行即可写入数据库,密码固定(直接修改此处即可)
k_tgs = "tgs123456"
k_tgs_hash = hash.encrypt(k_tgs)
r_tgs = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                          db=config.redis_db1_, password=config.redis_auth)
r_tgs.set("tgs", k_tgs_hash)

k_v = "ss123456"
k_v_hash = hash.encrypt(k_v)
r_v = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                        db=config.redis_db1_, password=config.redis_auth)
r_v.set("ss", k_v_hash)


def service_thread(_sock: socket.socket):
    """
    处理请求的函数(线程内运行)
    :param _sock: 收发报文对应的socket
    :return:
    """
    global log_txt
    log_txt += "收到新连接" + '\n'
    print("收到新连接", _sock)

    myPacket = mysocket.recv(_sock)
    # ticket = {"kc_v": "", "id_c": "", "ad_c": "", "id_v": "", "ts_4": "", "lifetime_4": "480"}
    # Authenticator_c = {"id_c": "", "ad_c": "", "ts_5": ""}

    if myPacket.pac_type != 3:  # 报文类型错误  c_t
        return False
    # 其他检查，例如时间戳

    pack_error = get_pack("t_c", state="server_error")  # 方便后面用

    """各种检查都结束之后，开始利用字段的内容"""
    # 获取内容字段，并转dict {"idv": "", "tgt": "", "Authenticator_c": ""}
    _content = dict(eval(myPacket.content))  # 无需解密
    log_txt += "tgs收到的原始报文(dict)：" + str(_content) + '\n'
    print("tgs收到的原始报文(dict)：", _content)

    # 获取tgt字段，{"kc_tgs": "", "id_c": "", "ad_c": "", "id_tgs": "", "ts_2": "", "lifetime_2": "480"}
    tgt_sec = _content["tgt"]  # 用ktgs解密 全局变量
    tgt = dict(eval(des2.decrypt(tgt_sec, k_tgs_hash)))
    log_txt += "解密后的tgt" + str(tgt) + '\n'
    print("解密后的tgt", tgt)

    kc_tgs = int(tgt["kc_tgs"])
    log_txt += "解析出来的kc_tgs：" + str(kc_tgs) + '\n'
    print("解析出来的kc_tgs：", type(kc_tgs), kc_tgs)

    ts_2 = tgt["ts_2"]  # 要验证

    # 获取Authenticator_c  {"id_c": "", "ad_c": "", "ts_5": ""}
    Authenticator_c_sec = _content["Authenticator_c"]  # 用kc_tgs解密 来自tgt内部
    Authenticator_c = dict(eval(des2.decrypt(Authenticator_c_sec, kc_tgs)))
    log_txt += "解密后的authentic为：" + str(Authenticator_c) + '\n'
    print("解密后的authentic为：", Authenticator_c)

    ts_3 = Authenticator_c["ts_3"]  # 验证ts_3

    # 验证

    # 生成ticket
    _publicKey, _privateKey = rsa2.newkeys(512)  # 生成要给client分发的公私钥对
    kc_v = des2.newkey()  # 生成一个kc_v

    # 注意这里adc、idc
    idc = tgt["id_c"]
    ticket = {"kc_v": kc_v, "id_c": idc, "ad_c": "adc", "id_v": "0001", "ts_4": "", "lifetime_4": "480",
              'publickey': str(_publicKey)}
    ticket_sec = des2.encrypt(str(ticket), k_v_hash)  # ticket用ktgs加密

    # 生成报文
    message4 = {"kc_v": kc_v, "idv": "idv", "ts_4": ts_3 + 1, "ticket": ticket_sec, "private_key": str(_privateKey)}
    message4_sec = des2.encrypt(str(message4), kc_tgs)

    # 发送含有ticket的报文
    # _packet4 = get_pack('t_c', content=str(message4))
    _packet4 = get_pack('t_c', state="success", content=message4_sec)

    mysocket.send(_sock, _packet4)  # 调用mysocket内的send函数进行发送

    log_txt += "ticket发送完成" + '\n'
    print("ticket发送完成！！！")
    log.debug(log_txt, path='./tgs_log/', log_name=str(idc) + '.txt')
    _sock.close()
    return True


if __name__ == '__main__':
    log.debug("tgs.main called")
    tgs_port = config.port_tgs  # tgs监听的端口
    tgs_addr = config.addr_tgs  # tgs监听的IP地址
    print(socket.gethostname())

    tgs_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
    tgs_Socket.bind((tgs_addr, tgs_port))  # 将套接字与端口号绑定起来
    tgs_Socket.listen(5)  # socket的”排队个数“为5 ！！！不是最大连接数

    while True:
        print("listening: ", tgs_addr, ":", tgs_port)
        new_sock, adress = tgs_Socket.accept()  # 这条命令是阻塞的
        threading.Thread(target=service_thread, args=(new_sock,)).start()  # 收到新的请求就直接投入新的线程并且开始运行
