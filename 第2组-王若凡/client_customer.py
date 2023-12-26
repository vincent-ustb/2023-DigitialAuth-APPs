# -*- coding: utf-8 -*-
# @Time : 2022/5/16 00:29
# @Author : cheney
# @File : customer_cc.py
# @Software: PyCharm
# @Site: www.cheney.cc

# 8.0.25 MySQL Community Server、Python 3.8、
import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')

import random
import pymysql
import socket
import threading
import des2
import hash
from packet import get_pack  # 用来打包
from packet import pack  # 用来解析报文
import time
import config
import mysocket
import tkinter as tk
import tkinter.messagebox
from tkinter import *
from tkinter.ttk import *
import packet_show as test_tkinter
import datetime

order_list = set()  # 当前购买的
cur_menu = []  # 当前的菜单
user_id = ''  # 登录的用户ID
user_pwd = ''  # 登录用户的密码
user_info = ['id', '姓名', '性别', '地址', '电话号码', '余额']
rest_money = 0  # 用户的余额
s_ss = socket.socket()
sessionkey_global = 0
privatekey_global = [0, 0]
publickey_global = [0, 0]

''' ==============================================================================================
以下是关于 主界面 的操作
=============================================================================================='''


def flush_info():
    """

    :return:
    """

    """从服务器查询最新消息并显示在控件上"""
    get_info = {"id": user_id}
    # packet_print_window.input_show('刷新')
    # print('刷新')
    # print('sessionkey_global', type(sessionkey_global),sessionkey_global)
    # print('privatekey_global', type(privatekey_global),privatekey_global)
    packet_get_info = get_pack("c_s", "user", "refresh", content=str(get_info),
                               sessionkey=sessionkey_global, privatekey=privatekey_global)
    # print('刷新请求报文', len(packet_get_info))
    packet_print_window.input_show('刷新')
    ret_send = mysocket.send(s_ss, packet_get_info, ack_flag=False)  # 注意判断发送的返回值
    packet_print_window.send_show("c_s", "user", "refresh", len(packet_get_info), content=str(get_info),
                                  sessionkey=sessionkey_global, privatekey=privatekey_global)
    if ret_send == -2:
        tk.messagebox.showerror(message='等待ACK超时')
        return
    elif ret_send == -1:
        tk.messagebox.showerror(message='报文发送失败')
        return

    ret = mysocket.recv(s_ss, sessionkey=sessionkey_global, publickey=publickey_global)
    packet_print_window.recv_show(ret)
    # print("状态：", ret.state)
    packet_print_window.input_show(str('状态为：' + str(ret.state)))
    packet_print_window.input_show(str(ret))
    # print(ret)
    # [('id', '姓名', '性别', '地址', '电话号码', '余额'), ('1001', 'Cheney', 'F', '南望山', '18055264512', 9826359)]
    # [('商店id', '食品id', '商店名称', '食物名称', '食物价格'), ('12110', '24001', '蜜雪冰城', '柠檬水', 4), ('12110', '24002', '蜜雪冰城', '杨枝甘露', 10), ('12110', '24003', '蜜雪冰城', '珍珠奶茶', 6), ('12110', '24004', '蜜雪冰城', '卡布奇诺', 8), ('12110', '88999', '蜜雪冰城', '测试商品', 88999), ('12111', '25001', '老乡鸡', '鸡汤', 58), ('12111', '25002', '老乡鸡', '牛肉面', 18), ('12111', '25003', '老乡鸡', '豆浆', 5), ('12111', '25004', '老乡鸡', '小笼包', 10), ('12111', '25005', '老乡鸡', '番茄炒蛋', 12), ('12112', '26001', '友谊快餐', '番茄鸡蛋盖浇饭', 12), ('12112', '26002', '友谊快餐', '卤肉饭', 11), ('12112', '26003', '友谊快餐', '鱼香肉丝盖浇饭', 18)]
    # [('订单id', '商家名称', '金额', '订单状态', '日期'), ('1', '蜜雪冰城', 15, '订单完成', datetime.datetime(2021, 7, 1, 20, 6, 30)), ('17', '长长久久饭店 ', 148, '正在配送', datetime.datetime(2021, 7, 6, 9, 2, 4)), ('18', '周黑鸭', 71, '订单完成', datetime.datetime(2021, 7, 6, 9, 2, 4)), ('2', '老乡鸡', 64, '订单完成', datetime.datetime(2021, 7, 1, 20, 6, 30)), ('22', '长长久久饭店 ', 2825, '正在出餐', datetime.datetime(2022, 4, 25, 20, 39, 44)), ('23', '蜜雪冰城', 5, '正在出餐', datetime.datetime(2022, 4, 25, 20, 39, 44)), ('24', '蜜雪冰城', 89024, '正在出餐', datetime.datetime(2022, 4, 26, 10, 58, 15)), ('25', '长长久久饭店 ', 1036, '正在配送', datetime.datetime(2022, 5, 12, 14, 1, 57)), ('26', '长长久久饭店 ', 1036, '订单完成', datetime.datetime(2022, 5, 12, 14, 2, 54)), ('27', '蜜雪冰城', 11, '正在出餐', datetime.datetime(2022, 5, 12, 14, 2, 54)), ('28', '蜜雪冰城', 17, '正在出餐', datetime.datetime(2022, 5, 12, 14, 3, 6)), ('29', '蜜雪冰城', 7, '正在出餐', datetime.datetime(2022, 5, 12, 15, 22, 32)), ('3', '长长久久饭店 ', 1889, '订单完成', datetime.datetime(2021, 7, 1, 20, 28, 17)), ('30', '长长久久饭店 ', 46, '正在出餐', datetime.datetime(2022, 5, 15, 16, 55, 14)), ('31', '蜜雪冰城', 23, '正在出餐', datetime.datetime(2022, 5, 15, 16, 55, 15)), ('32', '老乡鸡', 16, '正在出餐', datetime.datetime(2022, 5, 15, 16, 55, 15)), ('33', '友谊快餐', 42, '正在出餐', datetime.datetime(2022, 5, 15, 16, 55, 15)), ('34', '老乡鸡', 59, '正在出餐', datetime.datetime(2022, 5, 15, 16, 57, 21)), ('35', '老乡鸡', 77, '正在出餐', datetime.datetime(2022, 5, 15, 17, 7, 29)), ('4', '蜜雪冰城', 9, '正在出餐', datetime.datetime(2021, 7, 1, 20, 28, 17)), ('5', '周黑鸭', 41, '订单完成', datetime.datetime(2021, 7, 1, 20, 28, 17)), ('50', '周黑鸭', 5, '正在出餐', '0000-00-00 00:00:00'), ('51', '周黑鸭', 150, '正在出餐', datetime.datetime(2022, 5, 16, 22, 44, 22)), ('52', '长长久久饭店 ', 136, '正在出餐', datetime.datetime(2022, 5, 16, 22, 44, 22)), ('53', '蜜雪冰城', 16, '正在出餐', datetime.datetime(2022, 5, 16, 22, 44, 22)), ('54', '老乡鸡', 36, '正在出餐', datetime.datetime(2022, 5, 16, 22, 44, 23)), ('55', '友谊快餐', 36, '正在出餐', datetime.datetime(2022, 5, 16, 22, 44, 23)), ('6', '周黑鸭', 21, '正在配送', datetime.datetime(2021, 7, 5, 13, 29, 34)), ('7', '蜜雪冰城', 7, '正在出餐', datetime.datetime(2021, 7, 5, 13, 29, 34)), ('8', '长长久久饭店 ', 1889, '正在配送', datetime.datetime(2021, 7, 5, 13, 29, 34))]
    ret_list_content = list(eval(ret.content))

    # stste 4 菜单为空      5 订单为空    6 都空
    # recv_inf = []
    # recv_menu = []
    # recv_order = []
    if ret.state == 1 and len(ret_list_content) == 3:  # 收到正常返回的报文
        recv_menu = ret_list_content[1]
        recv_order = ret_list_content[2]
    elif int(ret.state) == 4:  # 菜单为空
        # recv_menu = ret_list_content[1][1]
        recv_menu = []
        recv_order = ret_list_content[1]
    elif int(ret.state) == 5:  # 订单为空
        recv_menu = ret_list_content[1]
        recv_order = []
        # recv_order = ret_list_content[2][1]
    elif int(ret.state) == 6:  # 都为空
        # recv_menu = ret_list_content[1][1]
        # recv_order = ret_list_content[2][1]
        recv_menu = []
        recv_order = []
    else:  # 异常处理
        tk.messagebox.showerror(message='从服务器获取到的报文state出错' + str(ret.state))
        return

    recv_inf = ret_list_content[0][1]
    if user_id != recv_inf[0]:
        tk.messagebox.showerror(message='从服务器获取到的ID不匹配')
        return
    global user_info
    user_info = list(recv_inf)
    packet_print_window.input_show(str('flush接收到的全部信息：' + str(ret.content)))
    # print("flush接收到的全部信息：", ret.content)

    """从服务器收取的信息接收完毕"""
    """finish"""
    packet_print_window.input_show(str("\nrecv_inf" + str(type(recv_inf)) + str(recv_inf)))
    packet_print_window.input_show(str("\nrecv_menu" + str(type(recv_menu)) + str(recv_menu)))
    # print("\nrecv_menu", type(recv_menu), recv_menu)
    packet_print_window.input_show(str("\nrecv_order" + str(type(recv_order)) + str(recv_order)))
    # print("\nrecv_order", type(recv_order), recv_order)

    # 刷新用户名
    total_username_show.set(recv_inf[1])
    # 刷新余额
    global rest_money
    rest_money = recv_inf[5]
    total_wallet_show.set(str(rest_money))

    # 将recv_menu保存到全局
    global cur_menu
    cur_menu = list(recv_menu)[1:]
    packet_print_window.input_show("\n保存到全局的菜单cur_menu ：" + str(cur_menu))
    # print("\n保存到全局的菜单cur_menu ：", cur_menu)

    # 刷新订单到控件上
    # 先清除旧的信息
    x = order_list_table.get_children()
    for item in x:
        order_list_table.delete(item)
    # 添加新的信息
    i = 0
    # recv_order：：('订单id', '商家名称', '金额', '订单状态', '日期')
    for row in list(recv_order)[0:]:  # 格式：店名、商品、价格
        i += 1
        order_list_table.insert('', 'end', values=row)

    # global My_Tk
    # My_Tk.insert_tv()

    return ret_list_content


def submit_order():
    """
    判断余额是否足够，够的话减去相应的金额， 插入订单表.修改 左下角已选 为0 ，刷新菜单。更新主界面
    :return:
    """
    global order_list
    total_cost = 0  # 该订单总金额
    if len(order_list) == 0:
        tk.messagebox.showerror(message='空订单')
        return 0
    for i in order_list:
        total_cost += cur_menu[i - 1][4]

    # print("提交的订单总价为" + str(total_cost))
    packet_print_window.input_show("提交的订单总价为" + str(total_cost))

    global rest_money
    if rest_money < total_cost:  # 如果余额不足
        tk.messagebox.showerror(message='余额不足，提交订单失败')
        return 0

    rest_money -= total_cost
    # 修改数据库余额
    packet_print_window.input_show(str("程序当前的菜单" + str(cur_menu)))
    packet_print_window.input_show(str("程序处理的订单" + str(order_list)))
    # print("程序当前的菜单", cur_menu)
    # print("程序处理的订单", order_list)

    """todo：给服务器发送订单的请求报文开始"""
    # 当前订单的编号在order_list内
    # 当前菜单对应编号是 cur_menu
    send_order = []
    for _num in order_list:
        # print("待提交待订单内商品：", cur_menu[_num])
        packet_print_window.input_show("待提交待订单内商品：" + str(cur_menu[_num]))
        send_order.append(cur_menu[_num][0:2])

    packet_send_order = get_pack("c_s", "user", "submit", content=str(send_order),
                                 sessionkey=sessionkey_global, privatekey=privatekey_global)
    ret_send = mysocket.send(s_ss, packet_send_order, ack_flag=False)
    packet_print_window.send_show("c_s", "user", "submit", len(packet_send_order), content=str(send_order),
                                  sessionkey=sessionkey_global, privatekey=privatekey_global)
    if ret_send == -2:
        tk.messagebox.showerror(message='等待ACK超时')
        return
    elif ret_send == -1:
        tk.messagebox.showerror(message='报文发送失败')
        return

    ret = mysocket.recv(s_ss, sessionkey=sessionkey_global, publickey=publickey_global)
    packet_print_window.recv_show(ret)
    if ret.sign == 1:  # 收到正常返回的报文
        tk.messagebox.showinfo(title="通知", message="提交成功！")
        total_wallet_show.set(str(rest_money))
    elif ret.state == 3:  # 其他
        tk.messagebox.showerror(message='订单提交服务器失败')
    else:  # 异常处理
        tk.messagebox.showerror(message='订单提交服务器反馈失败')
    """给服务器发送充值金额的请求报文结束"""

    # 已选列表清空
    order_list.clear()
    total_cost_show.set(str(len(order_list)))


def alter_info():  # 修改个人信息
    def commit_info_change():
        # 从控件获取用户的输入
        # altered_id = alter_new_id.get()
        altered_addr = alter_new_addr.get()
        altered_sex = alter_new_sex.get()
        altered_tel = alter_new_tel.get()
        # altered_pwd = alter_new_pwd_confirm.get()
        altered_name = alter_new_name.get()
        """给服务器发送修改信息的请求报文开始"""
        change_info = {"name": altered_name, "sex": altered_sex, "address": altered_addr,
                       "phonenumber": altered_tel}
        packet_charge_money = get_pack("c_s", "user", "modify_info", content=str(change_info),
                                       sessionkey=sessionkey_global, privatekey=privatekey_global)
        ret_send = mysocket.send(s_ss, packet_charge_money, ack_flag=False)
        packet_print_window.send_show("c_s", "user", "modify_info", len(packet_charge_money), content=str(change_info),
                                      sessionkey=sessionkey_global, privatekey=privatekey_global)
        if ret_send == -2:
            tk.messagebox.showerror(message='等待ACK超时')
            return
        elif ret_send == -1:
            tk.messagebox.showerror(message='报文发送失败')
            return

        ret = mysocket.recv(s_ss, sessionkey=sessionkey_global, publickey=publickey_global)
        packet_print_window.recv_show(ret)
        if ret.state == 1:  # 收到正常返回的报文
            packet_print_window.input_show("修改信息成功后，服务器的返回：" + str(ret.content))
            # print("修改信息成功后，服务器的返回：", ret.content)
            ret_content_list = list(list(eval(ret.content))[1])
            global user_info
            user_info[1] = ret_content_list[0]
            user_info[2] = ret_content_list[1]
            user_info[3] = ret_content_list[2]
            user_info[4] = ret_content_list[3]
            total_username_show.set(ret_content_list[0])
            tk.messagebox.showinfo(message="修改成功")
        elif ret.state == 3:  # 其他
            tk.messagebox.showerror(message=str(ret.content))
        else:  # 异常处理
            tk.messagebox.showerror(message="服务器返回错误")
        """给服务器发送修改信息的请求报文结束"""
        window_alter_info.withdraw()

    # 从数据库查询个人信息
    global user_info
    info = user_info  # ['id', '姓名', '性别', '地址', '电话号码', '余额'
    # info = ['1001', '1001', 'Cheney', 'F', '南望山', '18055264512', 9826359]
    """ finish"""
    # 新建修改信息界面
    window_alter_info = tk.Toplevel(main_window)
    window_alter_info.geometry('450x350')
    window_alter_info.title('查询/修改信息')
    # 用户名变量及标签、输入框
    alter_new_id = tk.StringVar()
    tk.Label(window_alter_info, text='ID：').place(x=10, y=25)
    tk.Label(window_alter_info, text=info[0] + ' ' * 30 + '不可更改').place(x=110, y=10)
    # tk.Entry(window_alter_info, textvariable=alter_new_id).place(x=250, y=10)
    '''# 密码变量及标签、输入框
    alter_pwd_old = tk.StringVar()
    tk.Label(window_alter_info, text='老密码：').place(x=10, y=50)
    tk.Label(window_alter_info, text='***').place(x=110, y=50)
    tk.Entry(window_alter_info, textvariable=alter_pwd_old, show='*').place(x=250, y=50)
    # 重复密码变量及标签、输入框
    alter_new_pwd_confirm = tk.StringVar()
    tk.Label(window_alter_info, text='新密码：').place(x=10, y=90)
    tk.Label(window_alter_info, text='***').place(x=110, y=90)
    tk.Entry(window_alter_info, textvariable=alter_new_pwd_confirm, show='*').place(x=250, y=90)'''
    # 姓名
    alter_new_name = tk.StringVar()
    tk.Label(window_alter_info, text='姓名').place(x=10, y=80)
    tk.Label(window_alter_info, text=info[1]).place(x=110, y=80)
    tk.Entry(window_alter_info, textvariable=alter_new_name).place(x=250, y=80)
    # 性别
    alter_new_sex = tk.StringVar()
    tk.Label(window_alter_info, text='性别(M/F)').place(x=10, y=135)
    tk.Label(window_alter_info, text=info[2]).place(x=110, y=135)
    tk.Entry(window_alter_info, textvariable=alter_new_sex).place(x=250, y=135)
    # 电话
    alter_new_tel = tk.StringVar()
    tk.Label(window_alter_info, text='电话').place(x=10, y=190)
    tk.Label(window_alter_info, text=info[4]).place(x=110, y=190)
    tk.Entry(window_alter_info, textvariable=alter_new_tel).place(x=250, y=190)
    # 住址
    alter_new_addr = tk.StringVar()
    tk.Label(window_alter_info, text='地址').place(x=10, y=245)
    tk.Label(window_alter_info, text=info[3]).place(x=110, y=245)
    tk.Entry(window_alter_info, textvariable=alter_new_addr).place(x=250, y=245)

    # 确认注册按钮及位置
    tk.Button(window_alter_info, text='确认修改', command=commit_info_change).place(x=250, y=290)
    # tk.Button(window_alter_info, text='退出', command=signtowcg).place(x=50, y=310)


def charge_money():
    def charge_money_in():
        money = charge_amount.get()
        if charge_amount.get() == "" or int(charge_amount.get()) <= 0:
            tk.messagebox.showerror('错误', '金额有误')
        global rest_money
        target_money = int(charge_amount.get()) + rest_money
        identify_pwd = charge_pwd.get()
        if user_pwd != identify_pwd:
            tk.messagebox.showerror('错误', '密码错误')
            return
        # 修改数据库余额 user_id, target_money
        """给服务器发送充值金额的请求报文开始"""
        charge_pwd_en = hash.encrypt(user_pwd)
        char_money = {"id": user_id, "passwd": charge_pwd_en, "money": money}
        packet_charge_money = get_pack("c_s", "user", "recharge", content=str(char_money),
                                       sessionkey=sessionkey_global, privatekey=privatekey_global)
        ret_send = mysocket.send(s_ss, packet_charge_money, ack_flag=False)
        packet_print_window.send_show("c_s", "user", "recharge", len(packet_charge_money), content=str(char_money),
                                      sessionkey=sessionkey_global, privatekey=privatekey_global)
        if ret_send == -2:
            tk.messagebox.showerror(message='等待ACK超时')
            return
        elif ret_send == -1:
            tk.messagebox.showerror(message='报文发送失败')
            return

        ret = mysocket.recv(s_ss, sessionkey=sessionkey_global, publickey=publickey_global)
        packet_print_window.recv_show(ret)
        if int(ret.state) == 1:  # 收到正常返回的报文
            rest_money = int(ret.content)
            packet_print_window.input_show("充值返回正常")
            # print("充值返回正常")
            total_wallet_show.set(str(rest_money))

        elif ret.state == 2:  # 其他
            tk.messagebox.showerror(message=str(ret.content))
        else:  # 异常处理
            tk.messagebox.showerror(message='充值返回异常')
            return
        """给服务器发送充值金额的请求报文结束"""

        # flush_info()
        tk.messagebox.showinfo(title="通知", message="充值成功！")
        window_charge_money.withdraw()

    # 首先需要读取用户的 充值金额 验证密码
    # 新建充值界面
    window_charge_money = tk.Toplevel(main_window)
    window_charge_money.geometry('350x200')
    window_charge_money.title('充值')
    # 充值金额
    charge_amount = tk.StringVar()
    tk.Label(window_charge_money, text='金额：').place(x=10, y=10)
    tk.Entry(window_charge_money, textvariable=charge_amount).place(x=100, y=10)

    # 密码变量及标签、输入框
    charge_pwd = tk.StringVar()
    tk.Label(window_charge_money, text='密码：').place(x=10, y=50)
    tk.Entry(window_charge_money, textvariable=charge_pwd, show='*').place(x=100, y=50)

    # 确认注册按钮及位置
    tk.Button(window_charge_money, text='确认充值', command=charge_money_in).place(x=180, y=80)


# 窗口
main_window = tk.Tk()
"""todo"""
global packet_print_window

packet_print_window = test_tkinter.PacketInterface(main_window)
# 1001,1001
"""程序内"""

main_window.title('外卖管理_主界面 1.0 ')
main_window.geometry('800x520')
main_window.withdraw()  # 实现主窗口隐藏

left_index = 640  # 保证控件左边对齐
# 标签 用户名密码
tk.Label(main_window, text='用户名:').place(x=left_index, y=15)
tk.Label(main_window, text='余  额:').place(x=left_index, y=55)
tk.Label(main_window, text='已选:').place(x=40, y=480)
tk.Label(main_window, text='最近的订单：').place(x=440, y=180)
# 下面是三个用来展示信息的StringVar
total_cost_show = tk.StringVar()  # 用于展示已选商品数量
tk.Label(main_window, textvariable=total_cost_show).place(x=70, y=480)
total_cost_show.set("当前为0")

total_wallet_show = tk.StringVar()  # 用于展示余额
tk.Label(main_window, textvariable=total_wallet_show).place(x=left_index + 40, y=55)

total_username_show = tk.StringVar()  # 用于展示用户名
tk.Label(main_window, textvariable=total_username_show).place(x=left_index + 40, y=15)

bt_charge = tk.Button(main_window, text='充值余额', height=1, width=16, command=charge_money)
bt_charge.place(x=left_index - 140, y=50)
bt_user_info = tk.Button(main_window, text='查询修改个人信息', height=1, width=16, command=alter_info)
bt_user_info.place(x=left_index - 140, y=10)
bt_submit = tk.Button(main_window, text='提交订单', height=1, width=10, command=submit_order)
bt_submit.place(x=250, y=480)
bt_flush_order = tk.Button(main_window, text='刷  新', height=1, width=10, command=flush_info)
bt_flush_order.place(x=700, y=120)

# def creat_order_list():  # 显示订单的控件 显示最近几个
columns = ['订单号', '商家名', '金额', '状态', '日期']
width_ord = [45, 70, 50, 70, 110]
order_list_table = Treeview(
    master=main_window,  # 父容器
    height=10,  # 表格显示的行数,height行
    columns=columns,  # 显示的列
    show='headings',  # 隐藏首列
)
t = 0
order_list_table.place(x=440, y=200)
for i in columns:
    order_list_table.heading(i, text=i)  # 定义表头
for i in columns:
    order_list_table.column(i, width=width_ord[t], minwidth=40, anchor=S, )  # 定义列
    t += 1


class My_Tk():
    def __init__(self):
        self.main_window = main_window
        # self.main_window.geometry('800x500')
        self.orm = {}
        self.create_button()
        self.create_heading()
        self.create_tv()
        # self.insert_tv()  # 进入时 刷新一次

    def create_button(self):
        Button(self.main_window, text='刷新菜单', command=self.insert_tv).pack()

    def create_heading(self, ):
        '''重新做一个treeview的头，不然滚动滚动条，看不标题'''
        heading_frame = Frame(self.main_window)
        heading_frame.place(x=15, y=30)

        # 填充用
        button_frame = Label(heading_frame, width=0.5)
        button_frame.place(x=10, y=60)
        # 全选按钮
        self.all_buttonvar = IntVar()
        self.all_button = Checkbutton(heading_frame, text='', variable=self.all_buttonvar, command=self.select_all)
        self.all_button.pack(side=LEFT)
        self.all_buttonvar.set(0)

        self.columns = ['店铺', '商品', '价格']
        self.widths = [100, 100, 100]

        # 重建tree的头
        for i in range(len(self.columns)):
            Label(heading_frame, text=self.columns[i], width=int(self.widths[i] * 0.16), anchor='center',
                  relief=GROOVE).pack(side=LEFT)

    def create_tv(self):
        # 放置 canvas、滚动条的frame
        canvas_frame = Frame(self.main_window, width=400, height=400)
        canvas_frame.place(x=10, y=60)

        # 只剩Canvas可以放置treeview和按钮，并且跟滚动条配合
        self.canvas = Canvas(canvas_frame, width=400, height=400, scrollregion=(0, 0, 400, 400))
        # self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        self.canvas.pack(side=LEFT)
        # 滚动条
        ysb = Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=ysb.set)
        ysb.pack(side=RIGHT, fill=Y)
        # ysb.place(x=500, height=400)  # 滚动条的位置
        # 鼠标滚轮滚动时，改变的页面是canvas 而不是treeview
        self.canvas.bind_all("<MouseWheel>",
                             lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # 想要滚动条起效，得在canvas创建一个windows(frame)！！
        tv_frame = Frame(self.canvas)
        self.tv_frame = self.canvas.create_window(0, 0, window=tv_frame, anchor='nw', width=400,
                                                  height=400)  # anchor该窗口在左上方

        # 放置button的frame
        self.button_frame = Frame(tv_frame)
        self.button_frame.pack(side=LEFT, fill=Y)
        Label(self.button_frame, width=3).pack()  # 填充用

        # 创建treeview
        self.tv = Treeview(tv_frame, height=10, columns=self.columns, show='headings')  # height好像设定不了行数，实际由插入的行数决定
        self.tv.pack(expand=1, side=LEFT, fill=BOTH)
        # self.tv.place()
        # 设定每一列的属性
        for i in range(len(self.columns)):
            self.tv.column(self.columns[i], widt=1, minwidth=self.widths[i], anchor='center', stretch=True)

        # 设定treeview格式
        self.tv.tag_configure('oddrow', font='Arial 12')  # 设定treeview里字体格式font=ft
        self.tv.tag_configure('select', background='SkyBlue', font='Arial 12')  # 当对应的按钮被打勾，那么对于的行背景颜色改变
        self.rowheight = 27  # tkinter里只能用整数
        Style().configure('Treeview', rowheight=self.rowheight)  # 设定每一行的高度

        # 设定选中的每一行字体颜色、背景颜色 (被选中时，没有变化)
        Style().map("Treeview",
                    foreground=[('focus', 'black'), ],
                    background=[('active', 'white')]
                    )
        self.tv.bind('<<TreeviewSelect>>', self.select_tree)  # 绑定tree选中时的回调函数

    def insert_tv(self):
        # 清空tree、checkbutton
        items = self.tv.get_children()
        [self.tv.delete(item) for item in items]
        self.tv.update()
        for child in self.button_frame.winfo_children()[1:]:  # 第一个构件是label，所以忽略
            child.destroy()

        # 重设tree、button对应关系
        self.orm = {}
        """todo 从服务器查询最新消息并显示在控件上"""
        global cur_menu  # 使用全局的菜单变量
        if len(cur_menu) == 0:
            flush_info()

        i = 0
        # cur_menu: ('商店id', '食品id', '商店名称', '食物名称', '食物价格')
        for row in cur_menu:  # 格式：店名、商品、价格
            i += 1
            tv_item = self.tv.insert('', i, values=row[2:], tags=('oddrow'))  # item默认状态tags

            ck_button = tkinter.Checkbutton(self.button_frame, variable=IntVar())
            ck_button['command'] = lambda item=tv_item: self.select_button(item)
            ck_button.pack()
            self.orm[tv_item] = [ck_button]

        # 每次点击插入tree，先设定全选按钮不打勾，接着打勾并且调用其函数
        self.all_buttonvar.set(1)
        self.all_button.invoke()
        order_list.clear()

        # 更新canvas的高度
        height = (len(self.tv.get_children()) + 1) * self.rowheight  # treeview实际高度
        self.canvas.itemconfigure(self.tv_frame, height=height)  # 设定窗口tv_frame的高度
        self.main_window.update()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))  # 滚动指定的范围

    def select_all(self):
        print("全选按钮")
        '''全选按钮的回调函数
           作用：所有多选按钮打勾、tree所有行都改变底色(被选中)'''
        for item, [button] in self.orm.items():
            a = eval("0x" + str(item[1:]))
            if self.all_buttonvar.get() == 1:
                button.select()
                self.tv.item(item, tags='select')
                order_list.add(a)
                # print("___全选")
            else:
                button.deselect()
                self.tv.item(item, tags='oddrow')
                if len(order_list) != 0:
                    order_list.remove(a)
                # print("___全不选")
        total_cost_show.set(str(len(order_list)))
        # print(order_list)

    def select_button(self, item):
        print("单 选 ", end="")
        print(item)
        a = eval("0x" + str(item[1:]))
        print(a)
        a = a % len(cur_menu)
        if a in order_list:
            order_list.remove(a)
        else:
            order_list.add(a)
        print(order_list)
        total_cost_show.set(str(len(order_list)))
        '''多选按钮的回调函数 作用：1.改变底色 2.修改all_button的状态'''
        button = self.orm[item][0]
        button_value = button.getvar(button['variable'])
        if button_value == '1':
            self.tv.item(item, tags='select')
        else:
            self.tv.item(item, tags='oddrow')
        self.all_button_select()  # 根据所有按钮改变 全选按钮状态

    def select_tree(self, event):
        '''tree绑定的回调函数
           作用：根据所点击的item改变 对应的按钮'''
        select_item = self.tv.focus()
        button = self.orm[select_item][0]
        button.invoke()  # 改变对应按钮的状态，而且调用其函数

    def all_button_select(self):
        '''根据所有按钮改变 全选按钮状态
            循环所有按钮，当有一个按钮没有被打勾时，全选按钮取消打勾'''
        for [button] in self.orm.values():
            button_value = button.getvar(button['variable'])
            if button_value == '0':
                self.all_buttonvar.set(0)
                break
        else:
            self.all_buttonvar.set(1)


My_Tk()
''' ==============================================================================================
以下是关于 登录界面 的操作
=============================================================================================='''

# 窗口
# loggin_window = tk.Tk()
loggin_window = tk.Toplevel(main_window)

loggin_window.title('外卖管理_用户登录界面 1.0 ')
loggin_window.geometry('350x500')
# 画布放置图片
canvas = tk.Canvas(loggin_window, height=250, width=250)
imagefile = tk.PhotoImage(file='../resource/logo_win.png')
image = canvas.create_image(0, 0, anchor='nw', image=imagefile)
canvas.pack(side='top')
canvas.place(x=50, y=25)
# 标签 用户名密码
tk.Label(loggin_window, text='用户ID:').place(x=60, y=310)
tk.Label(loggin_window, text='密  码:').place(x=60, y=350)

# 用户名输入框
var_usr_name = tk.StringVar()
entry_usr_name = tk.Entry(loggin_window, textvariable=var_usr_name)
entry_usr_name.place(x=130, y=310)
# 密码输入框
var_usr_pwd = tk.StringVar()
entry_usr_pwd = tk.Entry(loggin_window, textvariable=var_usr_pwd, show='*')
entry_usr_pwd.place(x=130, y=350)


# 退出的函数
def usr_sign_quit():
    loggin_window.destroy()
    exit()


def log_in(id1, password1):
    """
    被按钮响应函数调用的函数，用来注册（处理报文），因为响应函数传参和返回不方便
    :param id1:
    :param password1:
    :return: s_ss
    """
    password1_en = hash.encrypt(password1)
    # 连接AS服务器获取tgt
    s_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    '''addr_as = "127.0.0.1"
    port_as = 10001'''
    buffer_size = 1024
    address_as = (config.addr_as, config.port_as)

    # 开始连接AS服务器
    s_as.connect(address_as)
    ts1 = time.time()
    info2as = {"idc": id1, "passwd": password1_en, "id_tgs": 'tgs', "ts1": ts1}
    print(type(password1_en), password1_en)
    # msg2as = get_pack('c_a', 'user', 'get_ticket1', content=str(info2as))  # 改成str
    msg2as = get_pack('c_a', 'user', 'get_ticket1', content=str(info2as))  # 改成str
    packet_print_window.send_show('c_a', 'user', 'get_ticket1', len(msg2as), content=str(info2as))
    # a = pack(msg2as)
    packet_print_window.input_show('msg' + str(len(msg2as)) + str(msg2as))
    packet_print_window.input_show(str(info2as))
    # print('msg', len(msg2as), msg2as)
    # print(str(info2as))
    s_as.send(msg2as)
    """
    cnt = 0
    while True:
        a = s_as.recv(2048)
        cnt += 1
        print(">>", cnt, "---", pack(a).content)
    """
    msg2as_re = mysocket.recv(s_as)
    packet_print_window.recv_show(msg2as_re)
    # print('recv到了')
    packet_print_window.input_show(
        '接收到AS的消息' + str(len(msg2as_re.content)) + str(type(msg2as_re.content)) + str(msg2as_re.content))
    # print('接收到AS的消息', len(msg2as_re.content), type(msg2as_re.content), msg2as_re.content)
    packet_print_window.input_show('password1_en(client1的密钥): ' + str(type(password1_en)) + str(password1_en))
    # print('password1_en(client1的密钥): ', type(password1_en), password1_en)
    try:
        content_plain = des2.decrypt(msg2as_re.content, password1_en)
    except:
        # tk.messagebox.showerror(message='登录密码错误')
        return
    # print(msg2as_re.content)
    # print('>>>111:', type(k_c_hash), k_c_hash)
    # _content1 = dict(eval(msg2as_re.content))  # 没有拆
    # _text1 = _content1["tgt"]
    # text1 = dict(eval(des2.decrypt(str(_content1), k_c_hash)))
    packet_print_window.input_show('解密后:' + str(type(content_plain)) + str(content_plain))
    # print('解密后:', type(content_plain), content_plain)
    content_dic = dict(eval(content_plain))
    tgt = content_dic['tgt']
    ts2 = content_dic['ts_2']
    if int(msg2as_re.state) == 1 and ts2 == ts1+1:
        tk.messagebox.showinfo(title='成功', message='请求AS认证成功')
    else:
        tk.messagebox.showinfo(title='错误', message='请求AS认证失败')
        return
    '''if tgt is not None:
        tk.messagebox.showinfo(title='成功', message='请求AS认证成功')

    else:
        tk.messagebox.showinfo(title='错误', message='请求AS认证失败')
        return'''
    '''while True:
        ts1 = time.time()
        info2as = {"idc": id1, "passwd": password1_en, "id_tgs": 'tgs', "ts1": ts1}
        print(type(password1_en), password1_en)
        # msg2as = get_pack('c_a', 'user', 'get_ticket1', content=str(info2as))  # 改成str
        msg2as = get_pack('c_a', 'user', 'get_ticket1', content=str(info2as))  # 改成str
        # a = pack(msg2as)
        print('msg', len(msg2as), msg2as)
        print(str(info2as))
        s_as.send(msg2as)
        # msg2as_re = pack(s_as.recv(10240))
        # print(msg2as_re)
        # msg2as_re = pack(s_as.recv(10240))  # 接收AS服务器端发来的消息
        """
        cnt = 0
        while True:
            a = s_as.recv(2048)
            cnt += 1
            print(">>", cnt, "---", pack(a).content)
        """
        msg2as_re = mysocket.recv(s_as)
        # print('recv到了')
        print('接收到AS的消息', len(msg2as_re.content), type(msg2as_re.content), msg2as_re.content)
        print('password1_en(client1的密钥): ', type(password1_en), password1_en)
        try:
            content_plain = des2.decrypt(msg2as_re.content, password1_en)
        except:
            # tk.messagebox.showerror(message='登录密码错误')
            return
        # print(msg2as_re.content)
        # print('>>>111:', type(k_c_hash), k_c_hash)
        # _content1 = dict(eval(msg2as_re.content))  # 没有拆
        # _text1 = _content1["tgt"]
        # text1 = dict(eval(des2.decrypt(str(_content1), k_c_hash)))
        print('解密后:', type(content_plain), content_plain)
        content_dic = dict(eval(content_plain))
        tgt = content_dic['tgt']
        if tgt is not None:
            tk.messagebox.showinfo(title='成功', message='请求AS认证成功')
            break
        else:
            tk.messagebox.showinfo(title='错误', message='请求AS认证失败')
            return'''
    # kc_tgs = text["kc_tgs"]
    s_as.close()  # 关闭socket
    packet_print_window.input_show('as认证结束')
    # print('as认证结束')

    #  用tgt向TGS服务器获取st
    s_tgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address_tgs = (config.addr_tgs, config.port_tgs)
    #  开始连接TGS服务器
    s_tgs.connect(address_tgs)
    kc_tgs = int(content_dic["kc_tgs"])
    ts3 = time.time()
    lifetime = '480'
    authenticator = {"idc": id1, "ad_c": '', "ts_3": ts3, "Lifetime": lifetime}
    authenticator_c = des2.encrypt(str(authenticator), kc_tgs)
    info2tgs = {"idv": '', "tgt": tgt, "Authenticator_c": authenticator_c}
    msg2tgs = get_pack('c_t', 'user', 'request_ticket2', content=str(info2tgs))  # 这里C向TGS发送的消息
    mysocket.send(s_tgs, msg2tgs)
    packet_print_window.send_show('c_t', 'user', 'request_ticket2', len(msg2tgs), content=str(info2tgs))
    # s_tgs.(msg2tgs)
    packet_print_window.input_show('发给tgs的消息：' + '   ' + str(type(str(info2tgs))) + '   ' + str(info2tgs))
    # print('发给tgs的消息：', type(str(info2tgs)), str(info2tgs))
    # msg2tgs_re = pack(s_tgs.recv(buffer_size))  # 接收TGS发送回来的票据st
    # msg2tgs_re = s_tgs.recv(buffer_size)  # 接收TGS发送回来的票据st
    msg2tgs_re = mysocket.recv(s_tgs)
    packet_print_window.recv_show(msg2tgs_re)
    # print('未解密', type(msg2tgs_re.content), len(msg2tgs_re.content), msg2tgs_re.content)
    packet_print_window.input_show('密钥' + '   ' + str(type(kc_tgs)) + '   ' + str(kc_tgs))
    # print('密钥', type(kc_tgs), kc_tgs)
    content2_plain = des2.decrypt(msg2tgs_re.content, kc_tgs)
    content2_dic = dict(eval(content2_plain))
    # _text2 = _content2content2_dic
    # text2 = dict(eval(des2.decrypt(str(_content2), kc_tgs)))
    st = content2_dic["ticket"]
    # print("ticket", st)
    # kc_v = text2[""]
    ts4 = content2_dic["ts_4"]
    if int(msg2tgs_re.state) == 1 and ts4 == ts3+1:
        tk.messagebox.showinfo(title='成功', message='请求TGS认证成功')
    else:
        tk.messagebox.showinfo(title='错误', message='请求TGS认证失败')
        return
    '''if st is not None:
        tk.messagebox.showinfo(title='成功', message='请求TGS票据成功')
    else:
        tk.messagebox.showinfo(title='错误', message='请求TGS票据失败')
        return'''
    '''while True:
        kc_tgs = int(content_dic["kc_tgs"])
        ts3 = time.time()
        lifetime = '480'
        authenticator = {"idc": id1, "ad_c": '', "ts_3": ts3, "Lifetime": lifetime}
        authenticator_c = des2.encrypt(str(authenticator), kc_tgs)
        info2tgs = {"idv": '', "tgt": tgt, "Authenticator_c": authenticator_c}
        msg2tgs = get_pack('c_t', 'user', 'request_ticket2', content=str(info2tgs))  # 这里C向TGS发送的消息
        mysocket.send(s_tgs, msg2tgs)
        # s_tgs.(msg2tgs)
        print('发给tgs的消息：', type(str(info2tgs)), str(info2tgs))
        # msg2tgs_re = pack(s_tgs.recv(buffer_size))  # 接收TGS发送回来的票据st
        # msg2tgs_re = s_tgs.recv(buffer_size)  # 接收TGS发送回来的票据st
        msg2tgs_re = mysocket.recv(s_tgs)
        # print('未解密', type(msg2tgs_re.content), len(msg2tgs_re.content), msg2tgs_re.content)
        print('密钥', type(kc_tgs), kc_tgs)
        content2_plain = des2.decrypt(msg2tgs_re.content, kc_tgs)
        content2_dic = dict(eval(content2_plain))
        # _text2 = _content2content2_dic
        # text2 = dict(eval(des2.decrypt(str(_content2), kc_tgs)))
        st = content2_dic["ticket"]
        # print("ticket", st)
        # kc_v = text2[""]
        if st is not None:
            tk.messagebox.showinfo(title='成功', message='请求TGS票据成功')
            break
        else:
            tk.messagebox.showinfo(title='错误', message='请求TGS票据失败')
            break'''
    s_tgs.close()

    #  用st向V请求登录
    s_ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address_ss = (config.addr_ss, config.port_ss_client)
    # 开始连接SS服务器
    s_ss.connect(address_ss)
    # ticket = text2["ticket"]
    global sessionkey_global
    global privatekey_global
    sessionkey_global = int(content2_dic['kc_v'])  # 强制类型转换成了int
    privatekey_global = str(content2_dic["private_key"])
    # print(">>获取到私钥", type(private_key_ss), private_key_ss)
    ts5 = time.time()
    _authenticator2s = {"id_c": id1, "ad_c": '', "ts_5": ts5}
    authenticator2s = des2.encrypt(str(_authenticator2s), sessionkey_global)
    info2ss = {"ticket": st, "Authenticator_c": authenticator2s}
    msg2ss = get_pack('c_s', sign='user', control_type='message5', content=str(info2ss))
    packet_print_window.send_show('c_s', sign='user', control_type='message5', total_length=len(msg2ss), content=str(info2ss))
    packet_print_window.input_show('发送给ss的消息' + str(len(msg2ss)) + str(msg2ss))
    # print('发送给ss的消息', len(msg2ss), msg2ss)
    mysocket.send(s_ss, msg2ss)  # 分片发送
    # msg2ss_re = pack(s_ss.recv(buffer_size))
    # _content3 = dict(eval(msg2ss_re.content))
    msg2ss_re = mysocket.recv(s_ss)  # 分片接收
    packet_print_window.recv_show(msg2ss_re)
    _content3 = des2.decrypt(msg2ss_re.content, sessionkey_global)
    content3_dic = dict(eval(_content3))
    ts6 = content3_dic['ts6']
    global publickey_global
    publickey_global = content3_dic['pk_v']
    packet_print_window.input_show('publickey_global: ' + str(type(publickey_global)) + str(publickey_global))
    # print('publickey_global: ', type(publickey_global), publickey_global)
    if ts6 == ts5 + 1:
        tk.messagebox.showinfo(title='成功', message='登录成功')
    else:
        tk.messagebox.showinfo(title='失败', message='登录失败')
        return
    '''while True:
        global sessionkey_global
        global privatekey_global
        sessionkey_global = int(content2_dic['kc_v'])  # 强制类型转换成了int
        privatekey_global = str(content2_dic["private_key"])
        # print(">>获取到私钥", type(private_key_ss), private_key_ss)
        ts5 = time.time()
        _authenticator2s = {"id_c": id1, "ad_c": '', "ts_5": ts5}
        authenticator2s = des2.encrypt(str(_authenticator2s), sessionkey_global)
        info2ss = {"ticket": st, "Authenticator_c": authenticator2s}
        msg2ss = get_pack('c_s', sign='user', control_type='message5', content=str(info2ss))
        print('发送给ss的消息', len(msg2ss), msg2ss)
        mysocket.send(s_ss, msg2ss)  # 分片发送
        # msg2ss_re = pack(s_ss.recv(buffer_size))
        # _content3 = dict(eval(msg2ss_re.content))
        msg2ss_re = mysocket.recv(s_ss)  # 分片接收
        _content3 = des2.decrypt(msg2ss_re.content, sessionkey_global)
        content3_dic = dict(eval(_content3))
        ts6 = content3_dic['ts6']
        global publickey_global
        publickey_global = content3_dic['pk_v']
        print('publickey_global: ', type(publickey_global), publickey_global)
        if ts6 == ts5 + 1:
            tk.messagebox.showinfo(title='成功', message='登录成功')
            break
        else:
            tk.messagebox.showinfo(title='失败', message='登录失败')'''

    return s_ss


def usr_log_in():
    # 输入框获取用户名密码
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()
    if usr_pwd == "" or usr_pwd == "":
        tk.messagebox.showinfo(title='输入错误', message='用户名或密码为空')
        return
    global s_ss
    s_ss = log_in(usr_name, usr_pwd)
    if type(s_ss) == type(socket.socket()):  # 如果登陆成功
        tk.messagebox.showinfo(title='welcome', message='欢迎您：' + usr_name)
        global user_id  # 保存全局信息
        global user_pwd
        global sessionkey_global
        global privatekey_global
        global publickey_global
        user_id = usr_name
        user_pwd = usr_pwd
        loggin_window.destroy()
        main_window.deiconify()
        packet_print_window.input_show("登录界面被销毁，主界面打开")
        # print("登录界面被销毁，主界面打开\n")
        flush_info()
    else:
        tk.messagebox.showerror(message='密码错误')

    # # 用户名密码不能为空
    # elif usr_name == '' or usr_pwd == '':
    #     tk.messagebox.showerror(message='用户名或密码为空')
    # elif usr_name in other_user:
    #     tk.messagebox.showerror(message='账户类型出错，请切换其它系统')
    # # 不在数据库中弹出是否注册的框
    # else:
    #     is_signup = tk.messagebox.askyesno('欢迎', '您还没有注册，是否现在注册')
    #     if is_signup:
    #         usr_sign_up()


def usr_sign_up():
    # 确认注册时的相应函数
    def signtowcg():
        # 获取输入框内的内容
        n_id = new_id.get()
        n_pwd = new_pwd.get()
        n_pwd_c = new_pwd_confirm.get()
        n_name = new_name.get()
        n_sex = new_sex.get()
        n_tel = new_tel.get()
        n_addr = new_addr.get()

        if '' in [n_id, n_pwd, n_pwd_c, n_name, n_sex, n_tel, n_addr]:
            tk.messagebox.showerror('错误', '有内容为空')
            return
        elif not n_id.isdigit():
            tk.messagebox.showerror('错误', 'ID只能是数字')
            return
        elif n_pwd != n_pwd_c:
            tk.messagebox.showerror('错误', '密码前后不一致')
            return
        else:
            n_pwd_en = hash.encrypt(n_pwd)

        # 创建socket准备连接AS
        s_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address_as = (config.addr_as, config.port_as)
        # 开始连接AS服务器
        s_as.connect(address_as)
        packet_print_window.input_show(str(address_as))
        # print(address_as)
        info2as = {"id": n_id, "passwd": n_pwd_en}
        msg2as = get_pack('c_a', 'user', 'request_enroll', content=str(info2as))  # 请求注册的消息
        packet_print_window.send_show('c_a', 'user', 'request_enroll', len(msg2as), content=str(info2as))
        s_as.send(msg2as)
        # flag_as = s_as.recv(buffer_size)
        msg2as_re = mysocket.recv(s_as)
        packet_print_window.recv_show(msg2as_re)
        # print(flag_as)
        # msg2as_re = pack(flag_as)
        print(msg2as_re.state)
        if int(msg2as_re.state) != 1:
            tk.messagebox.showinfo(title='错误', message='AS注册失败')
            return
        else:
            tk.messagebox.showinfo(title='成功', message='AS注册成功')

        '''while True:
            info2as = {"id": n_id, "passwd": n_pwd_en}
            msg2as = get_pack('c_a', 'user', 'request_enroll', content=str(info2as))  # 请求注册的消息
            s_as.send(msg2as)
            # flag_as = s_as.recv(buffer_size)
            msg2as_re = mysocket.recv(s_as)
            # print(flag_as)
            # msg2as_re = pack(flag_as)
            print(msg2as_re.state)
            if int(msg2as_re.state) != 1:
                tk.messagebox.showinfo(title='错误', message='AS注册失败')
            else:
                tk.messagebox.showinfo(title='成功', message='AS注册成功')
                break'''
        s_as.close()  # 关闭与AS通信的socket

        # 创建socket准备连接SS
        s_ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address_ss = (config.addr_ss, config.port_ss_client)
        # 开始连接SS服务器
        s_ss.connect(address_ss)
        info2ss = {"id": n_id, "passwd": n_pwd_en, "name": n_name, "sex": n_sex, "address": n_addr,
                   "phonenumber": n_tel}
        msg2ss = get_pack('c_s', 'user', 'signature', content=str(info2ss))  # 请求注册的消息
        packet_print_window.send_show('c_s', 'user', 'signature', len(msg2ss), content=str(info2ss))
        packet_print_window.input_show(str(msg2ss))
        # print(msg2ss)
        s_ss.send(msg2ss)
        flag_ss = s_ss.recv(1024)
        packet_print_window.input_show(str(flag_ss))
        # print(flag_ss)
        msg2ss_re = pack(flag_ss)
        packet_print_window.recv_show(msg2ss_re)
        if int(msg2ss_re.state) != 1:
            tk.messagebox.showinfo(title='错误', message='SS注册失败')
            return
        else:
            tk.messagebox.showinfo(title='成功', message='SS注册成功')

            # while True:
            '''info2ss = {"id": n_id, "passwd": n_pwd_en, "name": n_name, "sex": n_sex, "address": n_addr,
                       "phonenumber": n_tel}
            msg2ss = get_pack('c_s', 'user', 'signature', content=str(info2ss))  # 请求注册的消息
            print(msg2ss)
            s_ss.send(msg2ss)
            flag_ss = s_ss.recv(1024)
            print(flag_ss)
            msg2ss_re = pack(flag_ss)
            if int(msg2ss_re.state) != 1:
                tk.messagebox.showinfo(title='错误', message='SS注册失败')
            else:
                tk.messagebox.showinfo(title='成功', message='SS注册成功')
                break'''
        # print('yes')
        s_ss.close()  # 关闭与SS通信的socket

        #  注册成功,摧毁注册界面
        tk.messagebox.showinfo('欢迎', "用户" + str(n_id) + '注册成功')
        window_sign_up.destroy()

    # 新建注册界面
    window_sign_up = tk.Toplevel(loggin_window)
    window_sign_up.geometry('350x350')
    window_sign_up.title('注册')
    # 用户名变量及标签、输入框
    new_id = tk.StringVar()
    tk.Label(window_sign_up, text='ID：').place(x=10, y=10)
    tk.Entry(window_sign_up, textvariable=new_id).place(x=150, y=10)
    # 密码变量及标签、输入框
    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='密码：').place(x=10, y=50)
    tk.Entry(window_sign_up, textvariable=new_pwd, show='*').place(x=150, y=50)
    # 重复密码变量及标签、输入框
    new_pwd_confirm = tk.StringVar()
    tk.Label(window_sign_up, text='确认密码：').place(x=10, y=90)
    tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*').place(x=150, y=90)
    # 姓名
    new_name = tk.StringVar()
    tk.Label(window_sign_up, text='姓名').place(x=10, y=130)
    tk.Entry(window_sign_up, textvariable=new_name).place(x=150, y=130)
    # 性别
    new_sex = tk.StringVar()
    tk.Label(window_sign_up, text='性别(M/F)').place(x=10, y=170)
    tk.Entry(window_sign_up, textvariable=new_sex).place(x=150, y=170)
    # 电话
    new_tel = tk.StringVar()
    tk.Label(window_sign_up, text='电话').place(x=10, y=210)
    tk.Entry(window_sign_up, textvariable=new_tel).place(x=150, y=210)
    # 住址
    new_addr = tk.StringVar()
    tk.Label(window_sign_up, text='地址').place(x=10, y=250)
    tk.Entry(window_sign_up, textvariable=new_addr).place(x=150, y=250)

    # 确认注册按钮及位置
    bt_confirm_sign_up = tk.Button(window_sign_up, text='确认注册',
                                   command=signtowcg)
    bt_confirm_sign_up.place(x=150, y=310)


def usr_mod_passwd():
    def ok_alt():
        # 获取用户输入 re_ 为修改后的信息
        id3 = id_alt.get()
        pwd3 = password_alt.get()
        pwd3_en = hash.encrypt(pwd3)  # hash加密后的密码
        print('pwd3_en', type(pwd3_en), pwd3_en)
        re_pwd = re_pwd_alt.get()
        re_pwd_en = hash.encrypt(re_pwd)
        print('re_pwd_en', type(re_pwd_en), re_pwd_en)
        '''re_name = name_alt.get()
        re_sex = sex_alt.get()
        re_phone = phone_alt.get()
        re_addr = address_alt.get()'''

        # 触发功能按钮

        # 创建socket准备连接AS
        s_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        '''addr_as = "127.0.0.1"
        port_as = 10001'''
        buffer_size = 1024
        address_as = (config.addr_as, config.port_as)
        # 开始连接AS服务器
        s_as.connect(address_as)
        info2as = {"id": id3, "passwd_old": pwd3_en, "passwd_new": re_pwd_en}
        msg2as = get_pack('c_a', 'user', 'modify_pwd', content=str(info2as))  # 请求修改的消息
        packet_print_window.send_show('c_a', 'user', 'modify_pwd', len(msg2as), content=str(info2as))
        s_as.send(msg2as)
        flag_as = s_as.recv(buffer_size)
        msg_re = pack(flag_as)
        packet_print_window.recv_show(msg_re)
        if int(msg_re.state) != 1:
            tk.messagebox.showinfo(title='错误', message='AS信息更改失败')
            return
        else:
            tk.messagebox.showinfo(title='成功', message='AS信息更改成功')
        '''while True:
            info2as = {"id": id3, "passwd_old": pwd3_en, "passwd_new": re_pwd_en}
            msg2as = get_pack('c_a', 'user', 'modify_pwd', content=str(info2as))  # 请求修改的消息
            s_as.send(msg2as)
            flag_as = s_as.recv(buffer_size)
            msg_re = pack(flag_as)
            if int(msg_re.state) != 1:
                tk.messagebox.showinfo(title='错误', message='AS信息更改失败')

            else:
                tk.messagebox.showinfo(title='成功', message='AS信息更改成功')
                break'''
        s_as.close()  # 关闭与AS通信的socket

        # 创建socket准备连接SS
        s_ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        '''addr_ss = "172.27.76.36"
        port_ss = 6969'''
        address_ss = (config.addr_ss, config.port_ss_client)
        # 开始连接SS服务器
        s_ss.connect(address_ss)
        info2ss = {"id": id3, "passwd_old": pwd3_en, "passwd_new": re_pwd_en}
        msg2ss = get_pack('c_s', 'user', 'modify_pwd', content=str(info2ss))  # 请求修改的消息
        packet_print_window.send_show('c_s', 'user', 'modify_pwd', len(msg2ss), content=str(info2ss))
        s_ss.send(msg2ss)
        flag_ss = s_ss.recv(buffer_size)
        msg_re = pack(flag_ss)
        packet_print_window.recv_show(msg_re)
        if int(msg_re.state) != 1:
            tk.messagebox.showinfo(title='错误', message='SS信息更改失败')
            return
        else:
            tk.messagebox.showinfo(title='成功', message='SS信息更改成功')

        '''while True:
            info2ss = {"id": id3, "passwd_old": pwd3_en, "passwd_new": re_pwd_en}
            msg2ss = get_pack('c_s', 'user', 'modify_pwd', content=str(info2ss))  # 请求修改的消息
            s_ss.send(msg2ss)
            flag_ss = s_ss.recv(buffer_size)
            msg_re = pack(flag_ss)
            if int(msg_re.state) != 1:
                tk.messagebox.showinfo(title='错误', message='SS信息更改失败')
            else:
                tk.messagebox.showinfo(title='成功', message='SS信息更改成功')
                break'''

        s_ss.close()  # 关闭与SS通信的socket

        alt_win.destroy()  # 销毁修改信息窗口

    alt_win = tk.Toplevel(loggin_window)
    alt_win.title('修改用户信息')
    alt_win.geometry('300x300+200+200')

    #  输入框， 输入旧密码和新密码，
    tk.Label(alt_win, text='ID(不可更改)').place(x=25, y=20)
    id_alt = tk.Entry(alt_win)
    id_alt.place(x=100, y=20)

    tk.Label(alt_win, text='旧密码').place(x=25, y=65)
    password_alt = tk.Entry(alt_win, show="*")
    password_alt.place(x=100, y=65)

    tk.Label(alt_win, text='新密码').place(x=25, y=110)
    re_pwd_alt = tk.Entry(alt_win, show="*")
    re_pwd_alt.place(x=100, y=110)

    # 按钮布置，确定 唤起功能按钮
    tk.Button(alt_win, text='确定', command=ok_alt).place(x=240, y=250)


# 登录 注册 退出三个按钮
bt_login = tk.Button(loggin_window, text='登录', command=usr_log_in)
bt_login.place(x=50, y=400)
bt_logup = tk.Button(loggin_window, text='注册', command=usr_sign_up)
bt_logup.place(x=110, y=400)
bt_logquit = tk.Button(loggin_window, text='退出', command=usr_sign_quit)
bt_logquit.place(x=170, y=400)
bt_mod_passwd = tk.Button(loggin_window, text='修改密码', command=usr_mod_passwd)
bt_mod_passwd.place(x=230, y=400)

if __name__ == '__main__':
    print('This is main in' + __name__)
    # main_window.deiconify()
    main_window.mainloop()

    print("用户成功登录进入系统")
