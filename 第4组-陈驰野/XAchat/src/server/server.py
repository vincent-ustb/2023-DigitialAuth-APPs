from socketserver import *
import pickle
import time
import utils
import ssl
import re
import database


# 功能描述：加载数据文件
def load(path):
    try:
        return pickle.load(open(path, 'rb'))
    except:
        return {}


class XAChatServer(ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate: bool = True) -> None:
        # 绑定数据库
        self.database = database.ServerDataBase()
        # 加载历史记录
        self.history = load('history.dat')

        # 创建SSL上下文
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        # 加载证书
        self.ssl_context.load_cert_chain(
            certfile="./certs/server.crt",
            keyfile="./certs/server.key"
        )
        self.ssl_context.check_hostname = False

        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

    def server_bind(self) -> None:
        # 将socket包装一层ssl
        self.socket = self.ssl_context.wrap_socket(self.socket, server_side=True, do_handshake_on_connect=True)
        super().server_bind()

    def server_close(self):
        self.socket.close()
        super().server_close()

    # 功能描述：注册用户
    def register(self, user, pwd) -> tuple[bool, str]:

        # 功能描述： 检测密码是否足够安全
        def is_safe(password: str) -> bool:
            # 检查口令长度是否足够长
            if len(password) < 8:
                return False
            # 检查口令是否包含数字、大写字母和小写字母
            if not re.search(r'\d', password) or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
                return False
            # 检查口令是否包含特殊字符
            if not re.search(r'[!@#$%^&*()_+{}|:\"\'<>,.?/~`]', password):
                return False
            # 如果口令通过所有检查，则返回True
            return True

        if user in self.database.get_users().keys():
            return False, "账号已存在"
        elif not is_safe(pwd):
            return False, "密码不够安全，应大于八位，且含有数字，大小写字母与特殊符号"
        else:
            self.database.add_users(user, utils.pwdhash(pwd))
            return True, ""

    # 功能描述：验证用户
    def validate(self, user, pwd) -> bool:
        users = self.database.get_users()
        if user in users.keys() and users[user] == utils.pwdhash(pwd):
            return True
        return False

    def get_key(self, u1, u2) -> tuple:
        return (u1, u2) if (u2, u1) not in self.history.keys() else (u2, u1)

    # 功能描述：每条聊天记录为key-value形式，key为（sender，receiver），value为（sender，time，msg）
    def append_history(self, sender, receiver, msg):
        if receiver == '':
            key = ('', '')
        else:

            key = self.get_key(sender, receiver)
        if key not in self.history.keys():
            self.history[key] = []
        self.history[key].append((sender, time.strftime('%m月%d日%H:%M', time.localtime(time.time())), msg))
        self.save_history()

    # 功能描述：把一条聊天记录存入内存中，返回某用户对某用户的聊天记录
    def get_history(self, sender, receiver):
        if receiver == '':
            key = ('', '')
        else:
            key = self.get_key(sender, receiver)
        return self.history[key] if key in self.history.keys() else []

    # 功能描述：将所有已注册用户的信息保存到文件中。
    def save_users(self) -> None:
        pickle.dump(self.users, open('users.dat', 'wb'))

    # 功能描述：将所有用户的所有聊天记录保存到文件中。
    def save_history(self):
        pickle.dump(self.history, open('history.dat', 'wb'))


# BaseRequestHandler类,可自动处理并发请求。
# 每有一个客户端请求连接时，都会new一个BaseRequestHandler类，然后在一个线程中处理相关请求。
class Handler(BaseRequestHandler):
    clients = {}

    def __init__(self, request, client_address, server) -> None:
        self.user = ''
        self.file_people = ''
        self.authed = False
        super().__init__(request, client_address, server)

    def setup(self):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "new client connect")

    def handle(self):
        while True:
            # 每次处理一个请求，每轮询间隔秒关闭，直到关机。
            data = utils.recv(self.request)
            # 未认证
            if not self.authed:
                try:
                    self.user = data['user']
                except:
                    pass
                # 服务端处理登录请求、注册请求、获取所有已登录用户的列表、获取连接中的用户与其他用户的聊天记录。
                if data['cmd'] == 'login':
                    if self.server.validate(data['user'], data['pwd']):
                        utils.send(self.request, {'response': 'ok'})
                        self.authed = True
                        for user in Handler.clients.keys():
                            # 加入在线列表
                            utils.send(Handler.clients[user].request, {'type': 'people_joined', 'people': self.user})
                        Handler.clients[self.user] = self
                    else:
                        utils.send(self.request, {'response': 'fail', 'reason': '账号或密码错误！'})
                # 服务端处理注册请求
                elif data['cmd'] == 'register':
                    flag, reason = self.server.register(data['user'], data['pwd'])
                    if flag:
                        utils.send(self.request, {'response': 'ok'})
                    else:
                        utils.send(self.request, {'response': 'fail', 'reason': reason})
            else:
                # 服务端获取所有已登录用户的列表
                if data['cmd'] == 'get_users':
                    users = []
                    for user in Handler.clients.keys():
                        if user != self.user:
                            users.append(user)
                    utils.send(self.request, {'type': 'get_users', 'data': users})
                # 服务端获取连接中的用户与其他用户的聊天记录。
                elif data['cmd'] == 'get_history':
                    utils.send(self.request, {'type': 'get_history', 'people': data['people'],
                                              'data': self.server.get_history(self.user, data['people'])})
                # 将连接中的用户的消息发给其期望接收的用户。
                elif data['cmd'] == 'chat' and data['people'] != '':
                    utils.send(Handler.clients[data['people']].request,
                               {'type': 'msg', 'people': self.user, 'msg': data['msg']})
                    self.server.append_history(self.user, data['people'], data['msg'])
                # 全局广播
                elif data['cmd'] == 'chat' and data['people'] == '':
                    for user in Handler.clients.keys():
                        if user != self.user:
                            # 广播
                            utils.send(Handler.clients[user].request,
                                       {'type': 'broadcast', 'people': self.user, 'msg': data['msg']})
                    self.server.append_history(self.user, '', data['msg'])
                elif data['cmd'] == 'close':
                    self.finish()

    def finish(self):
        if self.authed:
            self.authed = False
            if self.user in Handler.clients.keys():
                del Handler.clients[self.user]
            for user in Handler.clients.keys():
                utils.send(Handler.clients[user].request, {'type': 'people_left', 'people': self.user})


if __name__ == '__main__':
    # 能处理并发请求的服务端。服务端能处理并发请求，每当有客户端请求连接时，服务端都会开启一个线程进行处理。
    # 因此当有多个客户端同时请求服务时不会造成阻塞。
    app = XAChatServer(('127.0.0.1', 8888), Handler)
    # Handle one request at a time until shutdown
    app.serve_forever()
