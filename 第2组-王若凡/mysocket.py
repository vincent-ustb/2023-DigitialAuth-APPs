# -*- coding: utf-8 -*-
# @Time : 2022/5/12 15:01
# @Author : cheney
# @File : mysocket.py
# @Software: PyCharm
# @Site: www.cheney.cc

"""
这个程序原来实现大报文的传输，分片处理。
send2和recv2利用length字段来判断是否收取完毕
需要注意的是：连续收发对情况下，报文边界处理不当会导致报文收取不完整
"""

import socket
import dictionary
import log
from packet import pack
from packet import get_pack


def _get_dict_key(_dictionary, value):
    """
    辅助分片发送函数，根据dictionary找对应的值
    :param _dictionary:
    :param value:
    :return:
    """
    key = list(_dictionary.keys())[list(_dictionary.values()).index(value)]
    return key


def send2(_sock: socket.socket, packet: bytes) -> int:
    """
    发送报文
    :param _sock: 要传输的socket
    :param packet:  要发送的报文 get_pack的返回值
    :return: 返回成功发送的字节数目 -1 表示发送失败
    """
    cnt = 0
    MTU = 1024  # 最大传输单元
    # 首先判断要发送报文content字段的长度

    _mypacket = pack(packet)  # 解析成可识读的报文
    _content_total = _mypacket.content
    length_total = len(_content_total)
    rounds = int(length_total / MTU) + 1

    cnt = 0
    for i in range(rounds):  # 有几个1024就循环几次
        if i == rounds - 1:
            import time  # 调试用，用完删除
            time.sleep(1)  # 最后一片延时1s发送

            ret_content = str(_content_total[0 + MTU * i:])
            # ret_pack = get_pack(get_dict_key(dictionary.pac_type, _mypacket.pac_type), piece="0", content=ret_content, sign=get_dict_key(dictionary.sign, _mypacket.sign),
            #                     state=_mypacket.state, ack=_mypacket.ack, code_type=_mypacket.code_type,
            #                     control_type=_mypacket.control_type, src_id=_mypacket.src_id, dst_id=_mypacket.dst_id
            #                     )  # 0表示最后一个
            ret_pack = get_pack(_get_dict_key(dictionary.pac_type, format(_mypacket.pac_type, 'b').zfill(4)), piece="0",
                                content=ret_content)
            print(">>>发出第", i, "个分片：\n", ret_content)
            print(">>>头部:", ret_pack[0:12])
        else:
            ret_content = str(_content_total[MTU * i: MTU * (i + 1)])  # 截取当前轮次对应的内容
            ret_pack = get_pack(_get_dict_key(dictionary.pac_type, format(_mypacket.pac_type, 'b').zfill(4)), piece="1",
                                content=ret_content)  # 1表示后面还有
            print(">>>发出第", i, "个分片：\n", ret_content)
            print(">>>头部:", ret_pack[0:12])

        cnt += len(ret_content)
        _sock.send(ret_pack)  # 发送分片报文
        log.debug(str(ret_pack), path='./log/', log_name="send_packet.txt")
        print("本次使用socket发送了", len(ret_pack))
        # _sock.send(str("0"*512).encode())

    return cnt


def recv2(_sock: socket.socket) -> pack:
    """
    接收报文
    :param _sock: 要传输的socket
    :param packet:
    :return: 返回一个报文各个字段可以直接解析
    """
    content_total = ""
    packet_pieces = _sock.recv(1168)  # 收取1024+144
    packet_pieces_pack = pack(packet_pieces)

    cnt = 0
    while True:
        cnt += 1
        content_total += packet_pieces_pack.content  # 拼接多个content
        if str(packet_pieces_pack.piece) == "0":
            break
        else:
            packet_pieces = _sock.recv(1168)  # 收取1024+144
            packet_pieces_pack = pack(packet_pieces)
        print("收到第", cnt, "个分片:", packet_pieces_pack.content)

    packet_pieces_pack.content = content_total
    log.debug(content_total, path='./log/', log_name="recv_packet.txt")
    return packet_pieces_pack


def send(_sock: socket.socket, packet: bytes, sessionkey=None, publickey=None, ack_flag: bool = False,
         ack_time: int = 90) -> int:
    """
    发送报文的函数，可以实现大报文的分片发送，可以接收回执ack
    :param publickey:
    :param sessionkey:
    :param ack_flag: 是否需要等待回执ack
    :param ack_time:  等待ack超时的时间
    :param _sock:  要发送的socket
    :param packet:   要发送的报文
    :return: >0 表示成功发送的bit数，-1 表示发送失败， -2表示超时没有收到ack
    """
    # _sock.sendall(packet)

    # print("send2发送总长度:", len(packet), "length字段：", pack(packet).total_length)
    # if len(packet) != pack(packet).total_length + 168:  # 这里解析报文会导致速度很慢，调试完就把这三行删除！！！
    #     print(len(packet), pack(packet).total_length)
    #     raise ValueError("length != len(packet) - 168")
    # else:
    #     print("字段长度验证成功，from mysocket,send")

    log_txt2 = ''
    MTU = 1024
    length_total = len(packet)
    _round = int(length_total / 1024) + 1
    for i in range(_round):
        if i != _round - 1:
            content_send = packet[0 + MTU * i: MTU * (i + 1)]
            # _sock.send(content_send.zfill(1024))  # 少于1024 bit的补0补全
            # _sock.send(content_send.ljust(1024, b"0"))  # 0补在后面
            send_ret = _sock.send(content_send)  # 这是发送不补全的版本,
            log_txt2 += "第" + str(i + 1) + "次发送了:  " + "长度为： " + str(
                len(str(packet[0 + MTU * i: MTU * (i + 1)]))) + "的" + str(
                packet[0 + MTU * i: MTU * (i + 1)]) + "\n"
        else:  # 最后一次
            send_ret = _sock.send(packet[0 + MTU * i:])
            log_txt2 += "第" + str(i + 1) + "次发送了:  " + "长度为： " + str(len(str(packet[0 + MTU * i:]))) + "的" + str(
                packet[0 + MTU * i:]) + "\n"
        # print("send2第", i, "次发送了", send_ret)
    log_txt2 += "总长度为： " + str(len(packet))
    log.debug(log_txt2, path='./log/', log_name="send_packet.txt")

    if ack_flag:  # 判断如果需要回执ack
        print("》》》开始等待ack")
        ack_packet = recv(_sock, sessionkey=sessionkey, publickey=publickey)
        if ack_packet.ack != 1:  # 接收到的ack错误
            # return -2
            print(ack_packet.ack)
            raise ValueError("接收到的ack报文 ack字段不是1")
        else:
            print("成功验证ACK")

    return len(packet)  # 返回成功发送的bit数，表示发送成功而且收到ack


def recv(_sock: socket.socket, sessionkey=None, publickey=None, head_size: int = 168, piece_size: int = 1024,
         ack_flag: bool = False) -> pack:
    """
    根据length字段判别是否接收完毕
    :param ack_flag:  是否需要发送回执ack
    :param piece_size:  recv 每次接受的大小， 最小为1，最大为1024。越小越慢，越大越容易出错。
    :param head_size:  recv 第一次接受的大小，最小为报文头部大小，
    :param publickey: rsa非对称密钥
    :param sessionkey: des对称钥
    :param _sock:  要传输的socket
    :return: 返回一个报文对象，如果传入了密钥对话，content字段就是已经验证数字签名之后的内容。
    """
    _round = 1  # 收取信息的总次数
    msg_part = _sock.recv(head_size)  # 先收取一次
    if msg_part == b"":
        raise ValueError("发送方已经断开！")

    if not 1 <= piece_size <= 1024:
        raise ValueError("piece_size字段不在【1，1024】范围内")
    elif not 168 <= head_size <= 1024:
        raise ValueError("head_size字段不在【1，1024】范围内")

    cnt = len(msg_part)  # 当前收到的长度
    msg_total = msg_part
    length_total = int(pack(msg_part).total_length) + head_size  # 收至少一个报文头部大小的数据，解析出头部，获取length
    log_txt3 = ''
    log_txt3 += "recv2等待接收的总长度为" + str(length_total) + "\n"
    print("recv2等待接收的总长度为", length_total)
    # print("recv2第", _round, "接收到了", len(msg_part))
    while True:
        left_size = length_total - cnt  # 剩下的还没接收的长度

        if left_size > 0:  # 如果还没收完就继续
            if left_size >= piece_size:  # 如果当前剩下的要接收的内容，不满一个piece，那么就接收剩下的部分
                tmp = _sock.recv(piece_size)
            else:
                tmp = _sock.recv(left_size)

            if tmp == b"":
                raise ValueError("发送方已经断开！")

            cnt += len(tmp)  # 要接收的大小和实际接收的大小"不一定"一样。
            msg_total += tmp  # 加上实际获取到的内容

            log_txt3 += "recv2第" + str(_round) + "接收到了" + str(len(tmp)) + "cnt" + str(cnt)
            _round += 1
            # print("recv2第", _round, "接收到了", len(tmp), "cnt", cnt)
        else:
            log_txt3 += "\n 接收完毕"
            # print("接收完毕")
            break

    log.debug(log_txt3, path='./log/', log_name="recv_packet.txt")
    if len(msg_total) != length_total:
        raise ValueError("length指定的长度和实际收取长度不同！" + str(len(msg_total)) + "!=" + str(length_total))
    print("接收完毕,共计收到：", len(msg_total))

    if ack_flag:  # 判断如果需要回执ack
        ack_pack = get_pack("c_a", ack="YES", sessionkey=sessionkey, privatekey=publickey)
        send_ret = send(_sock, ack_pack)
        if send_ret > 0:
            print("发送回执ack成功")
        else:
            raise ValueError("发送回执ack失败")

    return pack(msg_total, sessionkey, publickey)


def flush(_sock: socket.socket) -> bool:
    """
    刷新缓冲区
    :param _sock:
    :return:
    """
    _sock.setblocking(False)
    while True:
        try:
            data = _sock.recvfrom(2048)
        except Exception as e:
            # print str(e)
            break
    _sock.setblocking(True)

    # 在这里recv(1),
    return True
