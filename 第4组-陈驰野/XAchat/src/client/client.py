import tkinter.filedialog
import tkinter.messagebox
import threading
import hashlib
import socket
import time
import ssl
import re

import utils
from window import LoginWin
from window import MainWin


class XAChatClient:
    def __init__(self) -> None:
        self.main_win = None
        self.socket = None
        self.user_name = ''
        self.current_session = ''
        self.users = {}

        # 设置服务端ip与端口
        self.server_ip = "127.0.0.1"
        self.server_port = 8888

        # 创建SSL上下文
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        # 加载证书
        self.ssl_context.load_verify_locations("./certs/ca.crt")
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED

        # 创建登录窗口
        self.login_win = LoginWin()
        self.login_win.btn_login.configure(command=self.on_btn_login_clicked)
        self.login_win.btn_reg.configure(command=self.on_btn_reg_clicked)
        self.login_win.show()

    # 功能描述；将socket库提供的套接字封装一层SSL
    def ssl_socket(self) -> ssl.SSLSocket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return self.ssl_context.wrap_socket(
            sock,
            server_side=False,
            do_handshake_on_connect=True,
            server_hostname=self.server_ip
        )

    # 客户端相关函数
    def close_socket(self):
        utils.send(self.socket, {'cmd': 'close'})
        self.socket.shutdown(2)
        self.socket.close()

    # 功能描述：登录按钮点击事件：当登录按钮点击时向服务端请求登录，如果登录成功则关闭登录页面，开启聊天页面。
    def on_btn_login_clicked(self):
        # 创建套接字
        self.socket = self.ssl_socket()
        self.socket.settimeout(5)
        try:
            if self.login_win.user.get() != '' and self.login_win.pwd != '':
                self.socket.connect((self.server_ip, self.server_port))
                utils.send(self.socket, {'cmd': 'login', 'user': self.login_win.user.get(),
                                         'pwd': self.login_win.pwd.get()})
                server_response = utils.recv(self.socket)
                if server_response['response'] == 'ok':
                    self.user_name = self.login_win.user.get()
                    # 销毁登录框
                    self.login_win.destroy()
                    self.main_win = MainWin()
                    self.main_win.closed_fun = self.close_socket

                    # 置顶欢迎
                    self.main_win.name.set('上午好!   %s' % self.user_name)
                    self.main_win.btn_send.configure(command=self.on_btn_send_clicked)
                    self.main_win.user_list.bind('<<ListboxSelect>>', self.on_session_select)
                    utils.send(self.socket, {'cmd': 'get_users'})
                    utils.send(self.socket, {'cmd': 'get_history', 'people': ''})

                    t = threading.Thread(target=self.recv_async, args=())
                    t.daemon = True
                    t.start()
                    self.main_win.show()
                elif server_response['response'] == 'fail':
                    tkinter.messagebox.showerror('警告', '登录失败：' + server_response['reason'])
                    self.close_socket()
            else:
                tkinter.messagebox.showerror('警告', '账号和密码不能为空！')
        except ssl.SSLCertVerificationError:
            tkinter.messagebox.showerror('警告', '服务端认证失败！')

    # 功能描述：注册按钮点击事件：当注册按钮点击时向服务端请求注册，得到回应后显示回应的消息（注册成功或注册失败、账号已存在等消息）。
    def on_btn_reg_clicked(self):
        self.socket = self.ssl_socket()
        self.socket.settimeout(5)
        try:
            if self.login_win.user.get() != '' and self.login_win.pwd.get() != '':
                self.socket.connect((self.server_ip, self.server_port))
                utils.send(
                    self.socket, {
                        'cmd': 'register',
                        'user': self.login_win.user.get(),
                        'pwd': self.login_win.pwd.get()
                    }
                )
                server_response = utils.recv(self.socket)
                if server_response['response'] == 'ok':
                    tkinter.messagebox.showinfo('注意', '注册成功！')
                elif server_response['response'] == 'fail':
                    tkinter.messagebox.showerror('警告', '注册失败：' + server_response['reason'])
            else:
                tkinter.messagebox.showerror('警告', '账号和密码不能为空！')
            self.close_socket()
        except ssl.SSLCertVerificationError:
            tkinter.messagebox.showerror('警告', '服务端认证失败！')

    def recv_async(self):
        while True:
            # 点击用户列表中的某用户时，显示与其一对一聊天的窗口。
            data = utils.recv(self.socket)
            if data == {}:
                return
            # 功能描述：刷新所有已登录用户列表：当开启聊天页面或收到服务端发来的新用户登录/登出的消息时刷新用户列表。
            if data['type'] == 'get_users':
                self.users = {}
                for user in [''] + data['data']:
                    self.users[user] = False
                self.refresh_user_list()
            # 功能描述：将聊天记录加入聊天记录显示框。
            elif data['type'] == 'get_history':
                if data['people'] == self.current_session:
                    # 历史记录管理
                    self.main_win.history['state'] = 'normal'
                    self.main_win.history.delete('1.0', 'end')
                    self.main_win.history['state'] = 'disabled'
                    for entry in data['data']:
                        self.append_history(entry[0], entry[1], entry[2])
            # 功能描述：当用户刚登录时显示世界聊天聊天记录，当用户点击其他用户与其一对一聊天时显示与其的聊天记录。
            elif data['type'] == 'people_joined':
                self.users[data['people']] = False
                self.refresh_user_list()
            # 功能描述：接收服务端消息函数。该函数运行在一个独立的线程中，不断接收服务端发来的消息。
            elif data['type'] == 'people_left':
                if data['people'] in self.users.keys():
                    del self.users[data['people']]
                if data['people'] == self.current_session:
                    self.current_session = ''
                    self.main_win.name.set('%s -> 世界聊天' % self.user_name)
                    self.users[''] = False
                    utils.send(self.socket, {'cmd': 'get_history', 'people': ''})
                self.refresh_user_list()
            elif data['type'] == 'msg':
                if data['people'] == self.current_session:
                    self.append_history(data['people'], time.strftime('%m月%d日%H:%M', time.localtime(time.time())),
                                        data['msg'])
                else:
                    self.users[data['people']] = True
                    self.refresh_user_list()
            elif data['type'] == 'broadcast':
                if self.current_session == '':
                    self.append_history(data['people'], time.strftime('%m月%d日%H:%M', time.localtime(time.time())),
                                        data['msg'])
                else:
                    self.users[''] = True
                    self.refresh_user_list()

    def refresh_user_list(self):
        self.main_win.user_list.delete(0, 'end')
        for user in self.users.keys():
            name = '世界聊天室' if user == '' else user
            # 未读消息
            if self.users[user]:
                name += ' (*)'
            self.main_win.user_list.insert('end', name)

    def append_history(self, sender, current_time, msg):
        self.main_win.history['state'] = 'normal'
        self.main_win.history.insert('end', '%s - %s\n' % (sender, current_time))
        self.main_win.history.insert('end', msg + '\n\n', 'text')
        self.main_win.history.see('end')
        self.main_win.history['state'] = 'disabled'

    def on_btn_send_clicked(self):
        if self.main_win.msg.get() != '':
            utils.send(self.socket, {'cmd': 'chat', 'people': self.current_session, 'msg': self.main_win.msg.get()})
            self.append_history(
                self.user_name,
                time.strftime('%m月%d日%H:%M', time.localtime(time.time())),
                self.main_win.msg.get()
            )
            self.main_win.msg.set('')
        else:
            tkinter.messagebox.showinfo('警告', '消息不能为空！')

    def on_session_select(self, event):

        w = event.widget
        changed = False
        if len(w.curselection()) != 0:
            index = int(w.curselection()[0])
            if index != 0:
                if self.current_session != w.get(index).rstrip(' (*)'):
                    changed = True
                    self.current_session = w.get(index).rstrip(' (*)')
                    self.main_win.name.set('%s -> %s' % (self.user_name, self.current_session))
                    self.users[self.current_session] = False
                    self.refresh_user_list()
            elif index == 0:
                if self.current_session != '':
                    changed = True
                    self.current_session = ''
                    self.main_win.name.set('%s -> global' % self.user_name)
                    self.users[''] = False
                    self.refresh_user_list()
            if changed:
                utils.send(self.socket, {'cmd': 'get_history', 'people': self.current_session})


if __name__ == '__main__':
    client = XAChatClient()
