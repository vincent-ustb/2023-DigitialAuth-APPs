# -*- coding: utf-8 -*-
# @Time : 2022/4/25 23:46
# @Author : cheney
# @File : as.py
# @Software: PyCharm
# @Site: www.cheney.cc

"""
AS（Authentication Server）= 认证服务器
TGS（Ticket Granting Server）= 票据授权服务器

AS运行运行逻辑：
as监听一个端口，当收到请求之后，就分配一个新的线程处理。
在这个线程内，对发出请求的客户端的信息进行验证，若验证成功则返回tgt给client，不成功则返回错误。
主线程一直监听新的请求。

功能函数：
    注册功能
    修改密码功能
    查询功能(查询是否在数据库)


注意互斥！！！
判断连接状态（recv返回值）
"""

import redis
import socket
import threading
import config  # 读取公共的配置信息 只需修改一处即可。
import des2
import log
import mysocket
import packet
import datetime
import time
from packet import get_pack  # 用来打包
from packet import pack  # 用来解析报文

log_txt = " "


def change_passwd(_sock: socket.socket, _user_id: str, _user_pas_old: str, _user_pas_new: str, sign: str) -> bool:
    """
    修改密码的函数
    :param _user_pas_old: 用户之前的密码
    :param _user_pas_new: 用户要修改的新密码
    :param sign: 用户类型标记
    :param _sock: 收发报文对应的socket
    :param _user_id: 用户的id
    :return: 是否更改失败
    """
    # print("请求修改密码", _sock)
    global log_txt
    log_txt += "用户:" + str(_user_id) + "请求修改旧密码" + str(_user_pas_old) + "为:" + str(_user_pas_new) + "\n"

    r = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                          db=config.redis_db0_, password=config.redis_auth)
    if r.get(_user_id) is None:
        # print("系统中无此用户", _user_id)
        log_txt += "系统中无用户" + _user_id + "\n"
        _sock.send(get_pack("a_c", state="server_error"))
        return False
    elif str(r.get(_user_id))[2:-1] != str(_user_pas_old):
        # print("数据库老密码", type(r.get(_user_id)), r.get(_user_id))
        # print("发来的老密码", type(_user_pas_old), _user_pas_old)
        # print("老密码验证失败", _user_id)
        log_txt += "旧密码登录不匹配" + "正确密码为：" + str(r.get(_user_id)) + "用户发送的密码为：" + str(_user_pas_old) + "\n"
        _sock.send(get_pack("a_c", state="server_error"))
        return False
    else:
        r.set(_user_id, _user_pas_new)  # 设置 name 对应的值
        # print("成功修改密码", _user_id)
        log_txt += "用户" + str(_user_id) + "修改密码成功" + "\n"
        _sock.send(get_pack("a_c", state="success"))
        return True


def register(_sock: socket.socket, _user_id: str, _user_pas: str, sign: str) -> bool:
    """
    请求注册的函数，断信息是否存在于数据库，如果存在则返回错误，不再则注册
    :param sign:  用户类型标记
    :param _sock:  收发报文对应的socket
    :param _user_id: 用户id
    :param _user_pas: 用户密码
    :return:
    """
    global log_txt
    log_txt += "用户：" + _user_id + "请求注册   " + "账号密码为：" + _user_pas + "\n"
    # print("请求注册", _sock)
    # print("账号密码：", _user_id, _user_pas)

    r = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                          db=config.redis_db0_, password=config.redis_auth)
    if r.get(_user_id) is not None:
        # print("已经存在该用户", _user_id)
        log_txt += "已经存在用户" + _user_id + "\n"
        _sock.send(get_pack("a_c", state="server_error"))
        return False
    else:
        r.set(_user_id, _user_pas)  # 设置 name 对应的值
        # print("成功注册", _user_id)
        log_txt += "用户：" + _user_id + "注册成功" + '\n'
        _sock.send(get_pack("a_c", state="success"))
        return True


def check_time(ts: float):
    timestamp = int(ts, 2)
    timenow = int(time.time())
    src_time = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    now_time = datetime.datetime.utcfromtimestamp(timenow).strftime("%Y-%m-%d %H:%M:%S")
    src_datetime = datetime.datetime.strptime(src_time, "%Y-%m-%d %H:%M:%S")
    now_datetime = datetime.datetime.strptime(now_time, "%Y-%m-%d %H:%M:%S")
    if (now_datetime - src_datetime).seconds > 60:
        print("有消息重放嫌疑")


def get_tgt(_sock: socket.socket, idc: str, id_tgs: str, ts1: str, sign: str) -> bool:
    """
    请求tgt的函数，验证成功则返回tgt,kerberos第一步交互的内容(1)C→AS:IDC ||IDtgs ||TS1
    :param sign: 用户类型标记
    :param ts1:
    :param id_tgs:
    :param idc:
    :param _sock: 收发报文对应的socket
    :return:
    """
    # 验证ts1

    # print("收到get tgt请求")
    global log_txt
    log_txt += "收到get tgt请求  " + "来自" + idc + '\n'
    # 访问数据库 1 得到k_tgs
    r = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                          db=config.redis_db1_, password=config.redis_auth)
    k_tgs_hash = r.get("tgs")
    if type(k_tgs_hash) == type(b""):
        # print("ktgs是byte已经转为str", k_tgs_hash)
        k_tgs_hash = str(k_tgs_hash)[2:-1]
    # print("成功获得K_tgs", ":", type(k_tgs_hash), k_tgs_hash)
    log_txt += "成功获得K_tgs: " + k_tgs_hash + '\n'
    # 访问数据库 0 得到k_c
    r = redis.StrictRedis(host=config.redis_addr, port=config.redis_port,
                          db=config.redis_db0_, password=config.redis_auth)
    k_c_hash = r.get(idc)
    if type(k_c_hash) == type(b""):
        # print("kc是byte已经转为str", k_c_hash)
        k_c_hash = str(k_c_hash)[2:-1]

    log_txt += "成功获得Kc: " + str(k_c_hash) + '\n'
    # print("成功获得Kc", idc, ":", type(k_c_hash), k_c_hash)
    # print("收到的k_tgs:", type(k_tgs_hash), k_tgs_hash)

    # 验证一下ts1，确保ts1小于当前时间并且相差不大于一分钟

    # 处理
    log_txt += "用户" + idc + "请求认证" + '\n'
    # print("请求认证", _sock)
    # 下面构造一个tgt
    kc_tgs = str(des2.newkey())
    # ts2 = "时间"
    ts2 = ts1 + 1
    _tgt = {"kc_tgs": kc_tgs, "id_c": idc, "ad_c": "", "id_tgs": id_tgs, "ts_2": ts2, "lifetime_2": "480"}
    log_txt += "返回tgt：" + str(_tgt) + '\n'
    # print("返回tgt：", _tgt)
    _tgt_sec = des2.encrypt(str(_tgt), k_tgs_hash)  # message2用ktgs加密，来自数据库
    log_txt += "返回tgt_sec为：" + _tgt_sec + '\n'
    # print("返回的tgt_sec：", _tgt_sec)
    # 然后包含tgt的报文的数据字段
    message2 = {"kc_tgs": kc_tgs, "id_tgs": id_tgs, "ts_2": ts2, "lifetime": "480", "tgt": _tgt_sec}
    # print("构造出的message2", message2)
    # 然后构造整个报文
    message2_sec = des2.encrypt(str(message2), str(k_c_hash))  # message2用Ekc加密，来自数据库
    # message2_sec = des2.encrypt(str(message2), "12345678")  # message2用Ekc加密，来自数据库
    log_txt += "加密后的message2为：" + str(message2_sec) + "长度为：" + str(len(message2_sec)) + '\n'
    log_txt += "用kc对content加密成功" + "kc为：" + str(k_c_hash) + '\n'
    # print("加密后的message2为", len(message2_sec), type(message2_sec), message2_sec)
    # print("用kc对content加密成功：", str(k_c_hash))
    _packet2 = get_pack('a_c', state="success", content=message2_sec)
    # print(">>>Conetet", type(message2_sec), message2_sec)
    mysocket.send(_sock, _packet2)

    return True


def service_thread(_sock: socket.socket):
    """
        收到新的连接，先判断该连接的类型，然后交给对应的服务函数处理
        :param _sock: 收发报文对应的socket
        :return:
        """
    global log_txt
    log_txt += "收到新连接" + '\n'
    print("收到新连接", _sock)
    message = _sock.recv(10240)  # 接收来自client的信息
    # print(threading.current_thread().getName(), " Accepted", adress, ":", message)  # 输出接收的信息
    log_txt += "接收到的信息为" + str(message) + '\n'
    myPacket = pack(message)  # 解析报文
    # print("pack初步解析后的报文：", myPacket, "***", myPacket.content)

    if myPacket.pac_type != 1:  # 报文类型错误
        log_txt += "报文类型验证失败c_a" + myPacket.pac_type + '\n'
        # print("报文类型验证失败c_a", myPacket.pac_type)
        return False
    else:
        log_txt += "报文类型验证成功c_a" + str(myPacket.pac_type) + '\n'
        # print("报文类型验证成功c_a")

    """各种检查都结束之后，开始利用字段的内容"""
    req_type = myPacket.control_type  # 首先从message中处理出字段
    sign = myPacket.sign
    log_txt += "第一个连接请求密文content" + myPacket.content + '\n'
    # print("第一个连接请求密文content", type(myPacket.content), myPacket.content)
    _content = dict(eval(myPacket.content))

    log_txt += "》》》开始调用功能函数" + '\n'
    # print("》》》开始调用功能函数")
    # 将日志写入目录为as_log，路径名为用户id.txt的文件中
    if int(req_type) == 2:  # 请求注册
        user_id_log = str(_content["id"])
        user_id = _content["id"]
        user_pas = _content["passwd"]
        register(_sock, user_id, user_pas, sign)
        log.debug(log_txt, path='./as_log/', log_name=user_id_log + '.txt')
    elif int(req_type) == 3:  # 修改密码
        # modify_pwd_as = {"id": "", "passwd_new": "", "passwd_old": ""}
        user_id_log = str(_content["id"])
        user_id = _content["id"]
        user_pas_new = _content["passwd_new"]
        user_pas_old = _content["passwd_old"]
        change_passwd(_sock, user_id, user_pas_old, user_pas_new, sign)
        log.debug(log_txt, path='./as_log/', log_name=user_id_log + '.txt')
    elif req_type == 1:  # 请求tgt
        user_id_log = str(_content["idc"])
        _idc = _content["idc"]
        _id_tgs = _content["id_tgs"]
        _ts1 = _content["ts1"]
        get_tgt(_sock, _idc, _id_tgs, _ts1, sign)
        log.debug(log_txt, path='./as_log/', log_name=user_id_log + '.txt')
    else:  # 没有这个服务
        log_txt += "请求功能号出错" + req_type + '\n'
        # print("请求功能号出错", req_type)
        # raise


if __name__ == '__main__':
    log.debug("as.main called")
    as_port = config.port_as  # as监听的端口
    as_addr = config.addr_as  # as监听的IP地址
    # print(socket.gethostname())

    as_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
    as_Socket.bind((as_addr, as_port))  # 将套接字与端口号绑定起来
    as_Socket.listen(5)  # socket的”排队个数“为5 ！！！不是最大连接数

    while True:
        print("listening: ", as_addr, ":", as_port)
        new_sock, adress = as_Socket.accept()  # 这条命令是阻塞的
        threading.Thread(target=service_thread, args=(new_sock,)).start()  # 收到新的请求就直接投入新的线程并且开始运行
