import struct
import json
from hashlib import sha256
import random
import string

max_buff_size = 1024


# 功能描述：对密码取sha256哈希
def pwdhash(pwd: str) -> str:
    return sha256(pwd.encode("UTF-8")).hexdigest()


# 功能描述: 发送数据前会在数据前部加上指明数据大小的一个二字节数。
def pack(data):
    # 打包为字节流，返回一个包装后的字符串。
    return struct.pack('>H', len(data)) + data


def send(socket, data_dict):
    socket.send(pack(json.dumps(data_dict).encode('utf-8')))


# 功能描述：接收数据时先接收这个二字节数，获取将要接收的数据包的大小，然后接收这个大小的数据作为本次接收的数据包。
def recv(socket):
    data = b''
    # pack打包，然后可以用unpack解包。
    surplus = struct.unpack('>H', socket.recv(2))[0]
    socket.settimeout(5)
    while surplus:
        recv_data = socket.recv(max_buff_size if surplus > max_buff_size else surplus)
        data += recv_data
        surplus -= len(recv_data)
    socket.settimeout(None)
    return json.loads(data)
