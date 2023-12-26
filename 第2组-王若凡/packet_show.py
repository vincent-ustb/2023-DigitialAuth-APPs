# -*- coding: utf-8 -*-
# @Time : 2022/5/15 16:07
# @Author : cheney
# @File : test_tkinter.py
# @Software: PyCharm
# @Site: www.cheney.cc
import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')

import threading
import time
import datetime
import tkinter as tk
import tkinter
from tkinter import *
from tkinter import scrolledtext
# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
# window
import packet
import des2
import rsa2

i = 0


class PacketInterface:
    def __init__(self, main_window: tkinter.Tk):
        # self.window = tk.Tk()
        self.window = tk.Toplevel(main_window)
        # window = ttk.Window()
        # style = ttk.Style("flatly")
        self.window.title("报文收发详情")
        self.window.geometry('800x650+450+0')
        # window.geometry('1200x750')
        # 得用绝对路径
        self.window.iconphoto(True, tk.PhotoImage(file='resource/windows_icon3.png'))

        self.frame = tk.Frame(self.window)
        self.frame.pack(fill=BOTH, expand=YES)

        # label
        label1 = Label(self.frame, text='收报文', width=8, height=1)  # 创建一个Label
        label1.place(x=35, y=4)
        label2 = Label(self.frame, text='发报文',  width=8, height=1)  # 创建一个Label
        label2.place(x=435, y=4)
        label3 = Label(self.frame, text='其他',  width=15, height=1)
        label3.place(x=35, y=450)
        # 收发窗口
        # 多行文本
        # 收报文
        self.text_input1 = scrolledtext.ScrolledText(self.frame, width=45, height=23)
        self.text_input1.pack(fill=BOTH, expand=YES)
        self.text_input1.place(x=35, y=26)

        # 发报文
        # text_input2 = scrolledtext.ScrolledText(frame, width=45, height=23)
        self.text_input2 = scrolledtext.ScrolledText(self.frame, width=45, height=23)
        # text_input2 = Text(frame, width=45, height=23)
        self.text_input2.pack(fill=BOTH, expand=YES)
        self.text_input2.place(x=435, y=26)

        # 输出用户输入
        self.text_input3 = scrolledtext.ScrolledText(self.frame, width=90, height=8)
        self.text_input3.pack(fill=BOTH, expand=YES)
        self.text_input3.place(x=80, y=475)
        # self.b = tk.Button(self.frame, text='清空', width=10, height=1, command=PacketInterface.flush(self)).place(x=370,
        #                                                                                                          y=450)
        # t = threading.Thread(target=PacketInterface.refreshText(self))  # 创建线程，不能使用target=dataget_main(52190805, 1, 0)
        # t.daemon = True  # 线程配置
        # t.start()  # 启动线程

    def recv_show(self, packet: packet.pack):
        # 插入数据
        # 新数据插在文本框开头
        self.text_input1.insert('1.0', "系统时间为：" + datetime.datetime.utcfromtimestamp(int(time.time())).strftime(
            "%Y-%m-%d %H:%M:%S") + '\n')
        self.text_input1.insert('2.0', "收到了一个长度为" + str(168 + packet.total_length) + "bits的报文" + '\n')
        # 输出为二进制，得转为具体类型
        self.text_input1.insert('3.0', "报文的流向为：" + str(packet.pac_type + packet.sign) + '\n')
        # 感觉没必要输出
        self.text_input1.insert('4.0', "报文的状态为：" + str(packet.state) + '\n')
        self.text_input1.insert('5.0', "报文请求为：" + str(packet.control_type) + '\n')
        self.text_input1.insert('6.0', "发送方id为：" + str(packet.get_src_id()) + '\n')
        self.text_input1.insert('7.0', "接收方id为：" + packet.get_dst_id() + '\n')
        self.text_input1.insert('8.0', "发送时间为：" + packet.get_src_time() + '\n')
        self.text_input1.insert('9.0', "除开报头的总长度为：" + str(packet.total_length) + '\n')
        self.text_input1.insert('10.0', "数据字段长度为：" + str(packet.length) + '\n' + "内容为：" + str(packet.content) + '\n'
                                + "---------------------------------------------\n")
        # text_input1.insert('insert', "---------------------------------------------\n")
        # print(self.get('0.0', "end"))

    def send_show(self, pac_type, sign, control_type, total_length: int, src_id="127.0.0.1", dst_id="127.0.0.1",
                  piece='0',
                  sessionkey=None,
                  privatekey=None, content='1', state='none', ack='NO', code_type='utf-8'):
        """
        将len(get_pack()的返回值)传给total_length
        """
        # 插入数据
        # 新数据插在文本框开头
        self.text_input2.insert('1.0', "系统时间为：" + datetime.datetime.utcfromtimestamp(int(time.time())).strftime(
            "%Y-%m-%d %H:%M:%S") + '\n')
        # 考虑把以下两句提出去
        # A = packet.GetHeader(pac_type, sign, control_type, src_id, dst_id, piece, sessionkey, privatekey,
        #                      content, state, ack, code_type)
        # packet1 = A.get_sec_packet()
        # self.text_input2.insert('2.0', "发送了一个长度为" + str(168 + int(packet1[144:168], 2)) + "bits的报文" + '\n')
        # 输出为二进制，得转为具体类型
        self.text_input2.insert('2.0', "发送了一个报文总长度为" + str(total_length) + "bits的报文" + '\n')
        self.text_input2.insert('3.0', "报文的流向为：" + str(pac_type) + '  ' + str(sign) + '\n')
        # 感觉没必要输出
        self.text_input2.insert('4.0', "报文的状态为：" + str(state) + '\n')
        self.text_input2.insert('5.0', "报文请求为：" + str(control_type) + '\n')
        self.text_input2.insert('6.0', "发送方id为：" + str(src_id) + '\n')
        self.text_input2.insert('7.0', "接收方id为：" + dst_id + '\n')
        # self.text_input2.insert('8.0', "发送时间为：" + datetime.datetime.utcfromtimestamp(int(A.get_src_time(), 2)).strftime(
        #     "%Y-%m-%d %H:%M:%S") + '\n')
        # # text_input2.insert('insert', "数据字段长度为：" + str(int(packet1[120:144], 2)) + '\n')
        # self.text_input2.insert('9.0', "除开报头的总长度为：" + str(int(packet1[144:168], 2)) + '\n')
        self.text_input2.insert('8.0', "数据字段长度为：" + str(len(content)) + '\n' + "内容为：" + str(
            content) + '\n' + "---------------------------------------------\n")
        # return packet1
        # text_input2.insert('insert', "---------------------------------------------\n")

    def input_show(self, content):
        self.text_input3.insert('1.0', "" + str(content) + '\n' +
                                "---------------------------------------------\n")
# '''
# if __name__ == "__main__":
#
#     publicKey, privateKey = rsa2.newkeys(512)
#
#     sessionKey = des2.newkey()
#
#     M = PacketInterface(main_window=tkinter.Tk())
#     A = packet.get_pack('c_a', 'none', 'unknown1', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
#                         privatekey=privateKey, content='3futu325fcn')
#
#     # P = pack(A.get_sec_packet(), sessionKey, publicKey)
#     P = packet.pack(A, sessionkey=sessionKey, publickey=publicKey)
#     # print(P)
#     M.send_show('c_s', 'business', 'unknown2', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
#                 privatekey=privateKey,
#                 content='3futu325fcn' * 9)
#     # M.send_show('c_s', 'business', 'unknown2', '127.0.0.1', '127.0.0.1', sessionkey=sessionKey,
#     #             privatekey=privateKey,
#     #             content='3futu325fcn' * 20)
#     M.recv_show(P)
#     M.window.mainloop()
#
#
#     # def flush(self):
#     #     self.text_input1.delete("1.0", "end")
#     #     self.text_input2.delete("1.0", "end")
#
#     # def refreshText(self):
#     #     global i
#     #     while 1:
#     #         i += 1
#     #         PacketInterface.send_show()
#     #         self.text_input1.update()
#     #         PacketInterface.send_show()
#     #         self.text_input2.update()
#     #         time.sleep(10)
#
#     # def Buttion(self):
#     #     b = tk.Button(self.frame, text='清空', width=10, height=1, command=PacketInterface.flush(self)).place(x=370, y=450)
#     #     return b
#
#
#
#
# roll2 = tk.Scrollbar(frame)
# roll2.pack(side=tk.RIGHT, fill=tk.Y)
# roll2.config(command=text_input2.yview)
# text_input2.config(yscrollcommand=roll2.set)
#
#
# # 一键清空当前文本框中内容，调用命令参数command=函数名
#
# # button = False
#
#
# # photoimage = photo.subsample(3,3)
# # 在窗口界面设置放置Button按键
#
# # b = ttk.Button(frame, text='清空', command=flush, bootstyle='success').place(x=370, y=450)
# # b.place(x=365, y=400)
# # c = packet.get_pack()
#
#
#
# #  界面
# from tkinter import ttk, S
#
#
# def insert():
#     info = [
#         ['C-A', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['A-C', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['A-T', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['C-T', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['T-C', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['T-V', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
#         ['V-T', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx']
#     ]
#     for index, data in enumerate(info):
#         table.insert('', tk.END, values=data)  # 添加数据到末尾
#
#
# def delete():
#     obj = table.get_children()
#
#
# msg_win = tk.Tk()
# msg_win.title('报文输出界面')
# screenwidth = msg_win.winfo_screenwidth()
# screenheight = msg_win.winfo_screenheight()
# width = 1000
# height = 500
# # x = int((screenwidth - width) / 2)
# # y = int((screenheight - height) / 2)
# msg_win.geometry('1000x300+650+350')
#
# columns = ['方向', '密文', '密文类型', '密文时间', '密文数据字段', '明文', '明文类型', '明文时间', '明文数据字段']
# table = ttk.Treeview(
#     master=msg_win,  # 父容器
#     height=10,  # 表格显示的行数
#     columns=columns,  # 显示的列
#     show='headings',  # 隐藏首列
# )
# #  定义表头
# table.heading(column='方向', text='方向', anchor='w', command=lambda: print('方向'))
# table.heading('密文', text='密文', )
# table.heading('密文类型', text='密文类型', )
# table.heading('密文时间', text='密文时间', )
# table.heading('密文数据字段', text='密文数据字段', )
# table.heading('明文', text='明文', )
# table.heading('明文类型', text='明文类型', )
# table.heading('明文时间', text='明文时间', )
# table.heading('明文数据字段', text='明文数据字段', )
#
# #  定义列
# table.column('方向', width=100, minwidth=100, anchor=S, )
# table.column('密文', width=100, minwidth=100, anchor=S)
# table.column('密文类型', width=100, minwidth=100, anchor=S)
# table.column('密文时间', width=100, minwidth=100, anchor=S)
# table.column('密文数据字段', width=100, minwidth=100, anchor=S)
# table.column('明文', width=100, minwidth=100, anchor=S)
# table.column('明文类型', width=100, minwidth=100, anchor=S)
# table.column('明文时间', width=100, minwidth=100, anchor=S)
# table.column('明文数据字段', width=100, minwidth=100, anchor=S)
# table.pack(pady=20)
#
# insert()
# f = tk.Frame(msg_win)
# f.pack()
# tk.Button(f, text='刷新', bg='pink', width=20, command=insert).pack(side=tk.LEFT)
#
# def show(jj,kk):
#     """
#     在显示控件内展示出报文
#     注意报文的格式！！！！！
#     :return:
#     """
#     pass
# '''
#  运行
