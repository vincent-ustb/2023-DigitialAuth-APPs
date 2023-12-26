import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')
import pymysql
import packet
from server import *
import server
import mysocket
import traceback
import log
import config

# 连接数据库
db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user, passwd=config.mysql_passwd,
                     db=config.mysql_db)
cursor = db.cursor()
ack_flag = False


def request_business(tcp_client, kc_v, pkc, SK, id, req_type: str, content: dict):
    """
        响应商家登陆后的请求
        :param tcp_client:socket
        :param kc_v: sessionkey
        :param pkc: C的公钥
        :param SK: V的私钥
        :param id:商家id
        :param req_type: 请求类型
        :param content: 解密后的报文内容
        :return:
    """
    # control_type6：对一些功能请求进行了修改

    # 修改个人信息:modify_info:0100////////////////////
    print("请求功能为：", int(req_type))
    if int(req_type) == 4:
        # id=content["id"]
        name = content["name"]
        address = content["address"]
        phonenumber = content["phonenumber"]
        modify_info(tcp_client, kc_v, pkc, SK, id, name, address, phonenumber)
    # 一键切换上下班'one_click_commuting': '0101',///////////
    elif int(req_type) == 5:
        # id=content["id"]
        one_click_commuting(tcp_client, kc_v, pkc, SK, id)
    # 刷新订单：'refresh——order': '0110'
    elif int(req_type) == 6:
        refresh_order(tcp_client, kc_v, pkc, SK, id)
    # 查看商品详情:product_details:0111///////////////
    elif int(req_type) == 7:
        product_details(tcp_client, kc_v, pkc, SK, id)
    # 修改商品信息:'modify_product': '1000',////////////////////
    elif int(req_type) == 8:
        # id_c=content["id"]
        id_d = content["id_d"]
        name = content["name"]
        price = int(content["price"])
        stock = int(content["stock"])
        modify_product(tcp_client, kc_v, pkc, SK, id_d, id, name, price, stock)
    # 添加商品'new_product': '1001',/////////////
    elif int(req_type) == 9:
        #
        # id_c = content["id"]
        id_d = content["id_d"]
        name = content["name"]
        price = int(content["price"])
        stock = int(content["stock"])
        new_product(tcp_client, kc_v, pkc, SK, id, id_d, name, price, stock)
    # 删除商品'delete_product': '1010',
    elif int(req_type) == 10:
        # id_c = content["id"]
        id_d = content["id_d"]
        delete_product(tcp_client, kc_v, pkc, SK, id, id_d)
    # 完成订单：finish_order:1011
    elif int(req_type) == 11:
        print("商家完成订单")
        finish_order(tcp_client, kc_v, pkc, SK, id, content)
    # 余额提现：cash_out:1100
    elif int(req_type) == 12:
        # id=content["id"]
        passwd = content["passwd"]
        money = int(content["money"])
        cash_out(tcp_client, kc_v, pkc, SK, id, passwd, money)

    return 0


# @@@@
def cash_out(tcp_client, kc_v, pkc, SK, id: str, passwd: str, money: int):
    """
    商家提现
    :param tcp_client: socket
    :param kc_v: sessionkey
    :param pkc:  C的公钥
    :param SK: V的私钥
    :param id: 商家id
    :param passwd: 商家id
    :param money: 提现金额
    :return:
    """
    log_txt = "商家提现\n"
    flag = server.__yanzheng(id, passwd, 2)
    if flag:
        show = "商家" + str(id) + "要提现" + str(money)
        log_txt += show + "\n"
        sql_cash_out = "SELECT Smoney FROM store WHERE Sno='" + id + "'"
        dict_info, result = server.sql_select(sql_cash_out)
        print(result)
        if money <= 0:
            print("输入有误")
            error_info = "金额输入不合法"
            log_txt += "商家金额输入不合法"
            mypack = packet.get_pack("s_c", sign="business", control_type='cash_out', state="server_error",
                                     content=str(error_info), sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack)
            log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
            return False
        print(type(money), money, type(result[0][0]), result[0][0])
        if result[0][0] >= money:
            print("够提现")
            sql_cash_update = "UPDATE store SET Smoney=" + str(result[0][0] - money) + " WHERE Sno='" + id + "'"
            server.sql_insert(sql_cash_update)
            sql_cash_out = "SELECT Smoney FROM store WHERE Sno='" + id + "'"
            print(sql_cash_out)
            dict_info, result1 = server.sql_select(sql_cash_out)
            print(str(ack_flag))
            if result1[0][0] == result[0][0] - money:
                print("余额更新成功")
                details = result1[0][0]
                log_txt += "商家金额提现成功\n"
                mypack = packet.get_pack("s_c", sign="business", control_type='cash_out', state="success",
                                         content=str(details), sessionkey=kc_v, privatekey=SK)
                mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
                return True
            else:
                print("提现失败")
                error_info = "提现失败"
                log_txt += "商家金额提现失败\n"
                mypack = packet.get_pack("s_c", sign="business", control_type='cash_out', state="server_error",
                                         content=str(error_info),
                                         sessionkey=kc_v, privatekey=SK)
                mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
        else:
            print("提现金额超过余额")
            error_info = "提现失败"
            log_txt += "商家金额提现失败,原因是提现金额超过余额\n"
            mypack = packet.get_pack("s_c", sign="business", control_type='cash_out', state="server_error",
                                     content=str(error_info),
                                     sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    else:
        print("密码输入有误")
        error_info = "密码输入有误"
        log_txt += "商家金额提现失败,原因是密码输入错误\n"
        mypack = packet.get_pack("s_c", sign="business", control_type='cash_out', state="server_error",
                                 content=str(error_info),
                                 sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')


def finish_order(tcp_client, kc_v, pkc, SK, id, content: list):
    """
    完成订单
    :param tcp_client: socket
    :param kc_v: sessionkey
    :param pkc:  C的公钥
    :param SK: V的私钥
    :param id_c: 商家id：str
    :param id_o: 订单id
    :return:
    """
    print(content)
    log_txt = "商家完成订单" + str(content)
    for i in range(len(content)):
        sql = "UPDATE orderr SET orderr.Ostate='正在配送' WHERE Ono='" + content[i] + "'"
        server.sql_insert(sql)
    mypack = packet.get_pack('s_c', sign='business', control_type='finish_order', state='success',
                             sessionkey=kc_v,
                             privatekey=SK)
    mysocket.send(tcp_client, mypack, ack_flag=ack_flag, sessionkey=kc_v, publickey=pkc)
    print("商家完成订单成功，报文发送成功")
    log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')


# @@@@
def delete_product(tcp_client, kc_v, pkc, SK, id_c: str, id_d: str):
    """
    删除商品
    :param tcp_client: socket
    :param kc_v: sessionkey
    :param pkc:  C的公钥
    :param SK: V的私钥
    :param id_c: 商家id：str
    :param id_d: 菜品id
    """
    sql = "SELECT * FROM WHERE Gno='" + id_d + "'"
    dict, results = server.sql_select(sql)
    if (len(results)) == 0:
        print("当前商品不存在")
        error_info = "当前商品不存在"
        mypack = packet.get_pack("s_c", sign="business", control_type='delete_product', state="server_error",
                                 content=str(error_info), sessionkey=kc_v,
                                 privatekey=SK)
        mysocket.send(tcp_client, mypack)
        return False
    sql = "DELETE FROM goods WHERE Gno='" + id_d + "' AND Sno='" + id_c + "'"
    server.sql_insert(sql)
    sql = "SELECT * FROM WHERE Gno='" + id_d + "'"
    dict, results = server.sql_select(sql)
    if (len(results)) == 0:
        print("当前商品不存在")
        mypack = packet.get_pack("s_c", sign="business", control_type='delete_product', state="success")
        mysocket.send(tcp_client, mypack)
        return False


# @@@@@
def new_product(tcp_client, kc_v, pkc, SK, id_c, id_d, name, price, stock):
    """
        添加商品
        :param tcp_client: socket
        :param kc_v: sessionkey
        :param pkc:  C的公钥
        :param SK: V的私钥
        :param id_c: 商家id：str
        :param id_d: 菜品id
        :param name: 菜品姓名
        :param price: 菜品价格
        :param stock: 菜品库存
        :return:
        """
    if '' in [id_c, id_d, name, price, stock]:
        print("有内容为空，添加商品失败")
        error_info = {"error_info": "有内容为空"};
        tcp_client.send(packet.get_pack("s_c", sign="business", control_type='new_product', state="server_error",
                                        content=str(error_info)))
        return False
    sql = "SELECT * FROM goods WHERE Gno='" + id_d + "'"
    dict, results = server.sql_select(sql)
    if (len(results)) > 0:
        print("此id已被使用")
        error_info = {"error_info": "id已被占用"};
        tcp_client.send(packet.get_pack("s_c", sign="business", control_type='new_product', state="server_error",
                                        content=str(error_info)))
        return False
    # 将信息插入数据库
    ins = '(\'{}\',\'{}\',\'{}\',{},{})'.format(id_d, id_c, name, price, stock)
    sql = "INSERT INTO goods VALUES " + ins
    print("添加新商品sql语句为:", sql)
    server.sql_insert(sql)
    print('添加商品成功')
    tcp_client.send(packet.get_pack("s_c", sign="business", control_type='new_product', state="success"))
    flag = True
    return flag


# @@@@
def modify_product(tcp_client, kc_v, pkc, SK, Gid: str, Sid: str, name: str, price: int, stock: int):
    """
    修改商品的信息
    :param tcp_client: socket
    :param kc_v: sessionkey
    :param pkc:  C的公钥
    :param SK: V的私钥
    :param Gid: 菜单id：str
    :param Sid: 商家id
    :param name: 菜品姓名
    :param price: 菜品价格
    :param stock: 菜品库存
    :return:
    """
    sql = "SELECT * FROM goods WHERE Gno='" + Gid + "' AND Sno='" + Sid + "'"
    print(sql)
    dict_, results = server.sql_select(sql)
    print(results)
    if len(results) != 0:
        # 修改信息
        change = 0
        sql_alt = "UPDATE goods SET"
        # 名字不为空
        if name != "":
            sql_alt += " Gname=\'" + name + " \'"
            change = 1
        if price != '':
            if change == 1:
                sql_alt += ","
            sql_alt += " Gprice=" + str(price)
            change = 1
        if stock != '':
            if change == 1:
                sql_alt += ","
            sql_alt += " Gstock=" + str(stock)
            change = 1
        sql_alt += " WHERE Gno=\'" + Gid + "\' AND Sno='" + Sid + "';"
        print("sql语句为:", sql_alt)
        server.sql_insert(sql_alt)
        # error_info = {"error_info": "有内容为空"};
        # tcp_client.send(packet.get_pack("s_c", sign="business", control_type='modify_product', state="server_error",
        #                                 content=str(error_info)), sessionkey=kc_v, privatekey=SK)
        print("执行了信息修改sql语句")
        sql = "SELECT Gname,Gprice,Gstock FROM goods WHERE Gno='" + Gid + "' AND Sno='" + Sid + "'"
        print(sql)
        dict_, results = server.sql_select(sql)
        print(results)
        if results[0][0] == name | results[0][1] == price | results[0][2] == stock:
            flag = True
            sql = "SELECT * FROM goods WHERE Gno='" + Gid + "'"
            print(sql)
            dict, results = server.sql_select(sql)
            print(results)
            info = results[0]
            print("用户当前信息为", info)
            product_info = {'name': '', 'Gprice': '', 'Gstock': ''}
            mypack = packet.get_pack('s_c', sign='business', control_type='modify_product', state='success',
                                     content=str(product_info), sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
        else:
            flag = False
            error_info = {"error_info": "信息修改失败"};
            mypack = packet.get_pack('s_c', sign='business', control_type='modify_product', state='server_error',
                                     content=str(error_info), sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    else:
        print("您的商店无此商品，请先注册")
        error_info = {"error_info": "商店无此商品，请注册"};
        mypack = packet.get_pack('s_c', sign='business', control_type='modify_product', state='server_error',
                                 content=str(error_info), sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
        flag = False
    return flag


def __refresh_left(id):
    sql = "SELECT orderr.Ono,customer.Cname,customer.Ctel,orderr.Omoney FROM orderr,customer WHERE orderr.Cno=customer.Cno AND orderr.Sno='" + id + "' AND orderr.Ostate='正在出餐'"
    dict, results = server.sql_select(sql)
    dict_info = ("订单id", "顾客姓名", "顾客电话", "订单金额")
    results = server.tuple_2_list(dict_info, results)
    return results


def __check_business_info(id):
    sql = "SELECT store.Sno,store.Sname,store.Saddr,store.Stel,store.Smoney,store.Sstate FROM  store WHERE Sno='" + id + "' "
    dict, results = server.sql_select(sql)
    dict_info = ("商家id", "店名", "地址", "电话号码", "营业额", "状态")
    results = server.tuple_2_list(dict_info, results)
    return results


def __refresh_right(id):
    sql = "SELECT orderr.Ono,store.Sname,orderr.Omoney,orderr.Ostate,orderr.OBtime FROM orderr,store WHERE orderr.Sno=store.Sno AND orderr.Sno='" + id + "'  order by orderr.OBtime desc limit 0,10"
    dict, results = server.sql_select(sql)
    dict_info = ("订单id", "商家名", "金额", "状态", "日期")
    results = server.tuple_2_list(dict_info, results)
    return results


def refresh_order(tcp_client, kc_v, pkc, SK, id: str):
    """
    刷新订单：返回订单号，收货人姓名，收货人电话，金额
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 商家id：str
    :return:
    """
    a = []
    log_txt = "商家提出刷新请求\n"
    print("商家刷新信息")
    content1 = __check_business_info(id)
    # print("商家个人信息为", content1)
    log_txt += "商家个人信息为:" + str(content1)
    a.append(content1)
    content2 = __refresh_left(id)
    # print("商家左边信息为", content2)
    log_txt += "商家未完成订单信息为:" + str(content2)
    content3 = __refresh_right(id)
    # print("骑手右边信息为", content3)
    log_txt += "商家最近订单信息为:" + str(content3)
    if (str(content2) != str(0)):
        a.append(content2)
    if (str(content3) != str(0)):
        a.append(list(content3))
    print(type(content3), type(content3))
    if (str(content3) == '0') and (str(content2) == str(0)):
        state = 'c'
    elif (str(content3) != str(0)) and (str(content2) != str(0)):
        state = 'success'
    elif (str(content2) == '0') and (str(content3) != str(0)):
        state = 'a'
    elif (str(content2) != '0') and (str(content3) == str(0)):
        state = "b"
    print("state为：", state)
    print("刷新时发送的内容为:", str(a))
    mypack = packet.get_pack('s_c', sign='business', control_type='refresh_order', state=state, content=str(a),
                             sessionkey=kc_v,
                             privatekey=SK)
    mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    print("刷新报文发送成功")
    log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
    return 0


def one_click_commuting(tcp_client, kc_v, pkc, SK, id: str):
    """
    一键切换上下班
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 商家id：str
    :return:
    """
    log_txt = "一键切换上下班\n"
    sql = "SELECT Sstate FROM Store WHERE Sno='" + id + "'"
    print("切换上下班执行的sql语句为：", sql)
    data_dict, results1 = server.sql_select(sql)
    print(results1)
    if results1[0][0] == '休息':
        print("当前商家在休息")
        sql = "UPDATE store SET Sstate='工作' WHERE Sno='" + id + "'"
        server.sql_insert(sql)
    else:
        print("当前商家在工作")
        sql = "UPDATE store SET Sstate='休息' WHERE Sno='" + id + "'"
        server.sql_insert(sql)
    sql = "SELECT Sstate FROM Store WHERE Sno='" + id + "'"
    data_dict, results = server.sql_select(sql)
    show = "商家" + results[0][0] + "了"
    # 发送报文
    # 报文内容
    log_txt += show
    if results[0][0] != results1[0][0]:
        log_txt += "商家一键上下班成功"
        mypack = packet.get_pack("s_c", sign="business", control_type='one_click_commuting', state="success",
                                 content=str(results[0][0]), sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag)
        log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
    else:
        log_txt += "商家一键上下班失败"
        mypack = packet.get_pack("s_c", sign="business", control_type='one_click_commuting', state="server_error",
                                 content=str("修改状态失败"), sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag, sessionkey=kc_v, publickey=pkc)
        log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')


def busi_sign(tcp_client, id_c: str, password: str, name: str, address: str, phonenumber: str, money: int, state="休息"):
    """
        商家注册
        :param id:商家id
        :param password:商家密码
        :param name: 商店名
        :param address: 商店地址
        :param phonenumber: 商店电话
        :param money: 营业额0
        :param state: 状态（休息/工作）
        :return:
    """
    # 添加用户信息
    # 有内容为空
    flag = False
    log_txt = "商家提出注册请求\n"
    if '' in [id_c, password, name, address, phonenumber]:
        print("有内容为空，注册失败")
        error_info = {"error_info": "有内容为空"};
        mypack = packet.get_pack("s_c", sign="business", state="server_error", content=str(error_info))
        mysocket.send(tcp_client, mypack)
    exist_user_info = []
    user_dict, results = server.select("password")
    sql = "SELECT Son FROM store"
    try:
        server.cursor.execute(sql)
        results = server.cursor.fetchall()
        print("results", results)
    except Exception:
        print("发生异常", Exception)
    flag = True
    for i in results:
        print(i[0], "\n")
        if id_c in exist_user_info:
            log_txt += "当前id已存在，注册失败"
            print("注册错误，用户id已存在")
            error_info = {"error_info": "用户id已存在"};
            mypack = packet.get_pack("s_c", sign="business", state="server_error", content=str(error_info))
            mysocket.send(tcp_client, mypack)
            flag = False
            break
    if flag:
        # 将信息插入数据库
        ins = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{})'.format(id_c, password, name, address, phonenumber, 10,
                                                                      "'休息'")
        sql = "INSERT INTO store VALUES " + ins
        print("注册sql语句为:", sql)
        server.sql_insert(sql)
        print('欢迎商家', id, '注册成功')
        log_txt += "商家注册成功"
        mypack = packet.get_pack("s_c", sign="business", state="success")
        mysocket.send(tcp_client, mypack)
        flag = True
    log.debug(log_txt, path='./server_log/business/', log_name=id_c + '.txt')
    return flag


def __if_success_alter(modify_name, modify_address, modify_phonenumber, name, address, phonenumber, id):
    print("修改信息为：", name, address, phonenumber)
    print("修改值为：", modify_name, modify_address, modify_phonenumber)
    sql = "SELECT Sname,Saddr,Stel FROM store WHERE Sno='" + id + "'"
    print(sql)
    dict_info, results = server.sql_select(sql)
    print("用户当前信息为", results[0][0], results[0][1], results[0][2])
    print("用户要修改的信息为：", name, address, phonenumber)
    print("修改值为：", modify_name, modify_address, modify_phonenumber)
    if (modify_name == 1 and name == results[0][0]) or modify_name == 0:
        print("姓名修改匹配")
        flag = True
    else:
        print("要修改的信息和修改后的信息不匹配1")
        return False

    if (modify_address == 1 and address == results[0][1]) or modify_address == 0:
        flag = True
    else:
        print("要修改的信息和修改后的信息不匹配3")
        return False
    if (modify_phonenumber == 1 and phonenumber == results[0][2]) or modify_phonenumber == 0:
        print("要修改的信息和修改后的信息匹配")
        return True
    else:
        print("要修改的信息和修改后的信息不匹配4")
        return False


# 修改个人信息
def modify_info(tcp_client, kc_v, pkc, SK, id: str, name: str, address: str, phonenumber: str):
    """
    商家修改信息
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 商家id：str
    :param name: 商店名：str
    :param address: 地址：str
    :param phonenumber: 电话：str
    :return: 返回修改信息是否正确
       """
    # 判断密码是否正确
    # print("旧密码为:",o_passwd)
    # flag=server.__yanzheng(id,o_passwd,2)
    log_txt = "商家提出修改信息请求\n"
    flag = True
    if flag:
        modify_name = 0
        modify_address = 0
        modify_phonenumber = 0
        # 修改信息
        change = 0
        sql_alt = "UPDATE store SET"
        # 名字不为空
        if name != "":
            sql_alt += " Sname=\'" + name + "\'"
            modify_name = 1
            change = 1
        # UPDATE customer SET Cpass='463c11fee9d44a34caa25b529da4fb6693573a0c42958cc5f5eaaacff94ca54a'
        # 地址不为空
        if address != "":
            if change == 1:
                sql_alt += ","
            sql_alt += " Saddr=\'" + address + "\'"
            modify_address = 1
            change = 1
        # 电话号码
        if phonenumber != "":
            if change == 1:
                sql_alt += ","
            sql_alt += " Stel=\'" + phonenumber + "\'"
            modify_phonenumber = 1
            change = 1
        sql_alt += "WHERE Sno=\'" + id + "\';"
        print("sql语句为:", sql_alt)
        server.sql_insert(sql_alt)
        print("信息修改成功")
        dict_info = ("name", "address", "phonenumber")
        flag = __if_success_alter(modify_name, modify_address, modify_phonenumber, name, address, phonenumber, id)
        if flag:
            print("信息修改成功")
            sql = "SELECT Sname,Saddr,Stel FROM store WHERE Sno='" + id + "'"
            print(sql)
            dict_info, results = server.sql_select(sql)
            log_txt += "信息修改成功\n"
            print("用户当前信息为", results)
            results = server.tuple_2_list(dict_info, results)
            print(results)
            mypack = packet.get_pack("s_c", sign="business", state="success", control_type="modify_info",
                                     content=str(results),
                                     sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack, ack_flag=ack_flag, sessionkey=kc_v, publickey=pkc)
        else:
            print()
            log_txt += "信息修改失败\n"
            mypack = packet.get_pack("s_c", sign="business", control_type='modify_info', state="server_error",
                                     content="修改后信息不匹配", sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack, ack_flag=ack_flag, sessionkey=kc_v, publickey=pkc)
            flag = False
        print("··································修改信息结束·······················")
    # else:
    #     print("客户的旧密码输入错误")
    #     error_info = {"error_info": "旧密码输入错误"};
    #     tcp_client.send(packet.get_pack("s_c", sign="business", control_type='modify_info',state="server_error", content=str(error_info),sessionkey=kc_v,privatekey=SK))
    #     flag=False
    log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
    return flag


def product_details(tcp_client, kc_v, pkc, SK, id: str):
    """
    查看商品详情:返回商品id，名称，单价，库存
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 商家id：str
    :return:
    """
    sql = "SELECT Gno,Gname,Gprice,Gstock FROM goods WHERE Sno='" + id + "'"
    dict_info, results = server.sql_select(sql)
    results = list(results)
    mypack = packet.get_pack("s_c", sign="business", control_type="product_details", state="success",
                             content=str(results), sessionkey=kc_v, privatekey=SK)
    mysocket.send(tcp_client, mypack, ack_flag=True, sessionkey=kc_v, publickey=pkc)

    return 0


def order_details():
    return 0
