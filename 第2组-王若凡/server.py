#服务器端
#多进程

import datetime
import os
import pymysql
import des2
import hash
import rsa2
import packet
import time
import socket
import config
import threading
import traceback
import mysocket
import server_deliver
from server_deliver import *
from server_business import *
from server_customer import *
from multiprocessing import Process
k_v="ss123456"
k_v_hash=hash.encrypt(k_v)
global PK
global SK
db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user, passwd=config.mysql_passwd, db=config.mysql_db)
cursor = db.cursor()

def runc():run(config.port_ss_client,recv_c)
def runb():run(config.port_ss_store,recv_c)
def rund():run(config.port_ss_deliver,recv_c)
#socket连接
def run(port,recv_c):
    """
    进程运行函数
    :param port: 监听端口 (port_ss_client,port_ss_store,port_ss_deliver)
    :param recv: 线程运行函数
    :return:
    """
    print("子进程开始>>pid={0},ppid={1}".format(os.getpid(), os.getppid()))
    time.sleep(2)
    # 创建tcp/ip协议的套接字
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.settimeout(6000)
    # 设置端口号复用，让程序推出端口号立即释放，否则的话在30秒-2分钟内这个端口不会被
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # host是服务器端的ip地址
    address = (config.addr_ss, port)
    print(address)
    # 绑定地址
    tcp_server.bind(address)
    # 设置监听
    tcp_server.listen(128)
    print("正在监听端口号为", port, "的端口")
    while True:
        tcp_client, tcp_client_addr = tcp_server.accept()
        print("已经连接到客户端，链接地址{0}".format(tcp_client_addr))
        """创建多线程对象并执行报文拆解函数，根据报文的拆解进行响应函数的调用"""
        thd = threading.Thread(target=recv_c, args=(tcp_client,))
        print("开启新线程")
        # 启动子线程对象
        thd.start()


def recv_c(tcp_client):
    """
    线程运行函数
    :param tcp_client:socket
    :return:
    """
    kc_v=''
    pkc=''
    while True:
        myPacket1=mysocket.recv(tcp_client)
        #myPacket1=tcp_client.recv(2048)
        print("收到报文,长度为:","内容为",myPacket1)
        #判断客户的类型是否是user,business,deliver
        # if int(myPacket1.sign)!=1 | int(myPacket1.sign)!=2 |int(myPacket1.sign)!=3:
        #     print("报文用户类别错误")
        #     continue
        #     #判断报文类别是否是c_s
        #myPacket1=packet.pack(myPacket1)
        if int(myPacket1.pac_type)!=5:
            print("报文类型错误")
            continue
        #读取字段内容，并转化为dict{“ticket”,"Authenticator_c"}
        # 得到请求字段
        req_type = myPacket1.control_type
        sign=myPacket1.sign
        #得到报文的数据字段
        print("得到的内容为：",myPacket1.content)
        content = dict(eval(myPacket1.content))
        print("server收到的原始报文内容为（dict）:", content)
        print("接收到的请求为：", int(req_type))
        #req_type:message5:0001
        if int(req_type) == 1:
            print("用户请求验证")
            flag,kc_v,pkc,id=authentic(tcp_client,content,sign)
            print("^^^^^^^^^^kc_v的类型为:",type(kc_v))
            print("^^^^^^^^^^^pkc的类型为:", type(pkc))
            print("^^^^^^^^^^^客户的id为:",id)
            print("用户请求验证",flag)
            print("sign=",sign)
            if flag:
                if int(sign)==1:
                    sort='user'
                    print("开始向客户端发送商品信息报文")
                # cust_check_info(tcp_client)
                    print(sort,"登陆成功")
                    break
                elif int(sign)==2:
                    sort='business'
                    print(sort,"登陆成功")
                    break
                elif int(sign)==3:
                    sort='deliver'
                    print(sort,"骑手登陆成功")
                    break
                else:
                    continue
            else:
                continue
        #注册信息:signature:0010
        elif int(req_type)==2:
            if int(sign)==1:
                print("客户注册")
                id = content["id"]
                passwd = content["passwd"]
                name = content["name"]
                sex = content["sex"]
                address = content["address"];
                phonenumber = content["phonenumber"]
                print("客户请求注册：", id, " ", passwd, " ", name, " ", sex, " ", address, " ", phonenumber, " ")
                flag = cust_sign(tcp_client,id, passwd, name, sex, address, phonenumber, 100);
                if flag:
                    continue
            elif int(sign)==2:
                print("商家注册")
                id = content["id"]
                passwd = content["passwd"]
                name = content["name"]
                address = content["address"];
                phonenumber = content["phonenumber"]
                print("商家请求注册：id：", id, "，passwd： ", passwd, " ，name:", name," ", "phonenumber ", phonenumber, " ")
                flag=busi_sign(tcp_client,id,passwd,name,address,phonenumber,0)
                if flag:
                    continue
            elif int(sign)==3:
                id = content["id"]
                print("骑手注册")
                passwd = content["passwd"]
                print("name")
                name = content["name"]
                print("sex")
                sex = content["sex"]
                print("phonenumber")
                phonenumber = content["phonenumber"]
                print("phonenumber2")
                print("骑手请求注册：", id, " ", passwd, " ", name, " ", sex, " ", phonenumber, " ",0)
                flag=deli_sign(tcp_client,id,passwd, name, sex, phonenumber, money=0, state = '休息')
                if flag:
                    continue
            else:
                print("类型错误,错误类型为",sign)
                continue
            #从报文获取信息

        #修改密码:client:modify_pwd:1010
        #business:0011
        #deliver:
        elif (int(req_type)==10) | (int(req_type)== 3):#修改密码
            print("客户修改密码")
            id = content["id"]
            print(id)
            print("参数的类型为",type(id))
            o_passwd=content["passwd_old"]
            print(o_passwd)
            n_passwd = content["passwd_new"]
            print(n_passwd)
            print("sign:",sign,"请求修改密码,id为：",id)
            flag = modify_pwd(tcp_client, id, int(sign), o_passwd, n_passwd)
            if flag:
                continue

    while True:
        #登录成功，开始进行操作
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&登陆成功了&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print("已登陆成功，开始接收用户的请求")
        try:
            mysocket.flush(tcp_client)
            client_text = mysocket.recv(tcp_client,sessionkey=kc_v,publickey=pkc)
            request(tcp_client,kc_v,pkc,SK,id,client_text)
        except ValueError:
            print("客户端下线")
            tcp_client.close()
            break


def authentic(tcp_client,content:dict,sort:str):
    """
    客户登录验证
    :param tcp_client:socket
    :param content:报文内容
    :param sort:客户类型（user，business，deliver）
    :return:flag，即验证是否成功
    """
    """
    content:dict类型
    对客户的信息进行验证
    C->V：Ticket v|| Authenticator
    Ticket v=Ekv[Kcv || IDc || ADc || IDv || TS4 || Lifetime4]
    Authenticator=Ekcv[IDc || ADc ||TS5]
    V->C:Ekcv[TS5+1]


    返回值：返回1.是否完成认证 2kcv（客户端和服务器段交互密钥）3 pkc（客户端的公钥，后续报文交互时需要数字签名）
    """
    log_txt="客户端请求认证\n"
    # 获取ticket字段
    # ticket={"kc_v": "", "id_c": "", "ad_c": "", "id_v": "", "ts_4": "", "lifetime_4": "480", 'publickey': ''}
    ticket_sec = content["ticket"]  # 用kcv解密，全局变量
    ticket = dict(eval(des2.decrypt(ticket_sec, k_v_hash)))
    print("解密后的ticket为：", ticket)
    log_txt += "解密后的ticket为:"+str(ticket)+"\n"
    # 获取kc_v
    kc_v = ticket["kc_v"]
    #pk_c：用户的公钥，后续进行数字签名验证
    pkc=ticket["publickey"]
    # 获取authenticator_c{"id_c": "", "ad_c": "", "ts_5": ""}
    Authenticator_sec = content["Authenticator_c"]
    Authenticator_c = dict(eval(des2.decrypt(Authenticator_sec, kc_v)))
    ts_5=Authenticator_c["ts_5"]
    print("解密后的authentic为：", Authenticator_c)
    log_txt += "解密后的authentic为:" + str(Authenticator_c) + "\n"
    #对报文的认证内容进行验证
    #获取tkv字段：Ekv[Kcv || IDc || ADc || IDv || TS4 || Lifetime4]
    sign=sort
    #进行验证
    if ticket["id_c"]==Authenticator_c["id_c"]:
            #& ticket["ts_4"]+1==Authenticator_c["ts_5"]:
        #验证通过,给客户端发送返回报文EKcv[TS5+1]
        #生成密钥
        print("验证通过")
        log_txt+="验证通过\n"
        global PK,SK
        PK,SK=rsa2.newkeys(512)
        ts6=ts_5+1;pk_v=PK;
        message={"pk_v":pk_v,"ts6":ts6}
        #用kcv对报文进行加密
        message_sec=des2.encrypt(str(message),kc_v)
        print("sort",type(sort),sort)
        if int(sort)==1:
            sort='user'
            print("sign=",sort,'客户登录')
            log_txt += sort+"登陆成功\n"
            sql_sign="SELECT * FROM customer WHERE Cno='"+ticket["id_c"]+"'"
            print("查的数据库为customer,语句为:",sql_sign)
            dict_sign,results=server.sql_select(sql_sign)
            if(len(results))>0:
                print(sort)
                mypack=packet.get_pack('s_c',sign=sort,control_type='message5',state='success',content=str(message_sec))
                mysocket.send(tcp_client,mypack)
                flag=True
            else:flag=False
        elif int(sort)==2:
            sort = 'business'
            print("商家登录")
            log_txt += sort + "登陆成功\n"
            sql_sign = "SELECT * FROM store WHERE Sno='" + ticket["id_c"] + "'"
            print("查的数据库为store,语句为:", sql_sign)
            dict_sign, results = server.sql_select(sql_sign)
            if (len(results)) > 0:
                mypack = packet.get_pack('s_c', sign=sort, control_type='message5', state='success',
                                     content=str(message_sec))
                mysocket.send(tcp_client, mypack)
                flag = True
            else:flag = False
            print(0)
        elif int(sort)==3:
            sort = 'deliver'
            print("骑手")
            log_txt += sort + "登陆成功\n"
            sql_sign = "SELECT * FROM deliverer WHERE Dno='" + ticket["id_c"] + "'"
            print("查的数据库为deliverer,语句为:", sql_sign)
            dict_sign, results = server.sql_select(sql_sign)
            if (len(results)) > 0:
                mypack = packet.get_pack('s_c', sign=sort, control_type='message5', state='success',
                                     content=str(message_sec))
                mysocket.send(tcp_client, mypack)
                flag = True
            else:flag = False
        #发送含有ticket的报文
        else:
            flag=False
            print("类型不存在")
        if flag:
            if int(sign) == 1:
                log.debug(log_txt, path='server_log\\customer\\', log_name=ticket["id_c"] + '.txt')
            elif int(sign) == 2:
                log.debug(log_txt, path='server_log\\business\\', log_name=ticket["id_c"] + '.txt')
            elif int(sign) == 3:
                log.debug(log_txt, path='server_log\\deliver\\', log_name=ticket["id_c"] + '.txt')
            return flag,kc_v,pkc,ticket["id_c"]
        else:
            log_txt += "认证失败"
            mypack = packet.get_pack('s_c', sign=sort, control_type='message5', state='server_error')
            mysocket.send(tcp_client, mypack)
            print("认证失败")
            if int(sign) == 1:
                log.debug(log_txt, path='server_log\\customer\\', log_name=ticket["id_c"]+ '.txt')
            elif int(sign) == 2:
                log.debug(log_txt, path='server_log\\business\\', log_name=ticket["id_c"]+ '.txt')
            elif int(sign) == 3:
                log.debug(log_txt, path='server_log\\deliver\\', log_name=ticket["id_c"] + '.txt')
            return False,0,0,0
    else:
        log_txt += "认证失败"
        mypack = packet.get_pack('s_c', sign=sort, control_type='message5', state='server_error')
        mysocket.send(tcp_client, mypack)
        print("认证失败")
        if int(sort) == 1:
            log.debug(log_txt, path='server_log/customer/', log_name=ticket["id_c"] + '.txt')
        elif int(sort) == 2:
            log.debug(log_txt, path='server_log/business/', log_name=ticket["id_c"] + '.txt')
        elif int(sort) == 3:
            log.debug(log_txt, path='server_log/deliver/', log_name=ticket["id_c"] + '.txt')
        return False, 0, 0, 0


def __yanzheng(id_c,passwd:str,sign:int):
    """
    用户验证:在充值余额和修改个人信息时需要对用户的密码进行验证
    :param id_c: 用户id
    :param passwd: 用户密码
    :param sign: 用户类型:1：client，2：business，3：deliver
    :return:
    """
    # 从数据库获取用户信息
    print("··························开始验证客户密码····································")
    print("验证用户输入的密码是否正确")
    sqlc = "SELECT Cpass FROM customer WHERE  Cno='" + id_c+"'"
    sqlb = "SELECT Spass FROM store WHERE  Sno='" + id_c + "'"
    sqld = "SELECT Dpass FROM deliverer WHERE  Dno='" + id_c + "'"
    if int(sign)==1:sql=sqlc;
    elif int(sign)==2:sql=sqlb;
    elif int(sign)==3:sql=sqld
    print("验证密码执行的sql语句为：",sql)
    print("密码的类型为:", type(passwd), "结果为：", passwd)
    data_dict, results = server.sql_select(sql)
    for row in results:
        print("结果的类型为:", type(row[0]), "结果为：", row[0])
        if row[0] == passwd:
            print("用户", id_c, "密码正确，验证通过")
            return True
    print("用户", id_c, "密码错误，验证不通过")
    return False
def modify_pwd(tcp_client, id:str,sign:int, o_passwd:str, n_passwd:str):
    """
    修改密码
    :param tcp_client:socket
    :param id: id
    :param sign:类型：1：client，2：business，3：deliver
    :param o_passwd: 旧密码
    :param n_passwd: 新密码
    :return: 是否修改成功
    """
    log_txt="客户修改密码\n"
    print("````````````````````````````````用户要修改密码```````````````````````````````````````````")
    if '' in [id,o_passwd,n_passwd]:
       print("有内容为空，修改密码失败")
       log_txt+="id，旧密码，新密码有空，修改密码失败\n"
       error_info = {"error_info": "有内容为空"};
       tcp_client.send(packet.get_pack("s_c", sign="user",state="server_error", content=str(error_info)))
    else:
    # 判断密码是否正确
        print("密码不为空")
        log_txt += "旧密码为："+str(o_passwd)+"\n"
        print('id为：',id,"旧密码为:", o_passwd)
        flag = __yanzheng(id, o_passwd,sign)
        print(2)
        if flag == False:
            log_txt += "旧密码不正确，修改密码失败\n"
            print("客户的旧密码输入错误")
            error_info = {"error_info": "旧密码输入错误"};
            tcp_client.send(packet.get_pack("s_c", sign="user", state="server_error", content=str(error_info)))
            if int(sign) == 1:
                log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
            elif int(sign) == 2:
                log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
            elif int(sign) == 3:
                log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')
            return False
        elif flag == True:
            # 修改信息
            #sql = "UPDATE customer SET Cpass='"+passwd+"'WHERE Cno='"+id+"'"
            sqlc = "UPDATE  customer SET Cpass='"+n_passwd+"' WHERE Cno='"+id+"'"
            sqlb = "UPDATE  store  SET  Spass='" + n_passwd+"' WHERE Sno='"+id+"'"
            sqld = "UPDATE deliverer SET  Dpass='" +n_passwd+"' WHERE Dno='"+id+"'"
            if int(sign) == 1:
                sql = sqlc;sort='user'
            elif int(sign) == 2:
                sql = sqlb;sort='business'
            elif int(sign) == 3:
                sql = sqld;sort='deliver'
            print("sql语句为:", sql)
            up_flag=server.sql_insert(sql)
            if up_flag:
                log_txt += "修改密码成功\n"
                tcp_client.send(packet.get_pack("s_c", sign=sort, control_type="modify_pwd",state="success"))
                flag = True
            else:
                print(sql + "失败", "修改失败")
                log_txt += "修改密码失败\n"
                tcp_client.send(packet.get_pack("s_c", sign=sort, control_type="modify_pwd",state="server_error", content="密码修改失败"))
                flag = False
            if int(sign) == 1:
                log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
            elif int(sign) == 2:
                log.debug(log_txt, path='./server_log/business/', log_name=id + '.txt')
            elif int(sign) == 3:
                log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')
            return flag


def Insert(table,par):
    sql="INSERT INTO %s VALUES %s;" % \
        (table,par)

    lock = threading.Lock()
    lock.acquire()

    try:#执行SQL语句
        print("执行的sql语句为：",sql)
        cursor.execute(sql)
        db.commit()
        print(sql+"成功")
    except:
        db.rollback()
        print(sql, "失败")
        print(traceback.format_exc())

    lock.release()

def select(table,par=''):
    #SQL查询语句
    lock = threading.Lock()
    lock.acquire()
    global cursor
    global db
    data_dict=[]
    results=[]
    sql="SELECT * FROM %s %s;" % \
        (table,par)
    try:
        cursor.execute(sql)
        results=cursor.fetchall()
        data_dict=[]
        for field in cursor.description:
            data_dict.append(field[0])
    except Exception:
        print(sql, "失败")
        print(traceback.format_exc())
    except:
        db.ping()
        db = db.cursor()
    lock.release()
    return data_dict,results

def sql_insert(sql):
    db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user, passwd=config.mysql_passwd, db=config.mysql_db)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception:
        print(sql, "失败")
        print(traceback.format_exc())
        return False
    except ConnectionAbortedError:
        db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user,
                             passwd=config.mysql_passwd,
                             db=config.mysql_db)
        cursor = db.cursor()
    except:
        db.ping()
        db = db.cursor()
    return True

def sql_select(sql:str):
    db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user,
                         passwd=config.mysql_passwd,
                         db=config.mysql_db)
    cursor = db.cursor()
    data_dict = []
    results = []

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for field in cursor.description:
            data_dict.append(field[0])
        db.commit()
    except Exception:
        print(traceback.format_exc())
        print("发生异常", Exception)
    except ConnectionAbortedError:
        db = pymysql.connect(host=config.addr_mysql, port=config.port_mysql, user=config.mysql_user,
                             passwd=config.mysql_passwd,
                             db=config.mysql_db)
        cursor = db.cursor()
    except:
        print(traceback.format_exc())
        db.ping()
        db = db.cursor()
    return data_dict,results

def main():
    """开启多进程监听三类客户"""
    c_pro = Process(target=runc)
    s_pro = Process(target=runb)
    d_pro = Process(target=rund)
    c_pro.start()
    s_pro.start()
    d_pro.start()

def request(tcp_client,kc_v,pkc,SK,id,client_text:bytes):
    thd = threading.Thread(target=request_client, args=(tcp_client,kc_v,pkc,SK,id,client_text,))
    print("功能请求：开启新线程")
    # 启动子线程对象
    thd.start()
    return 0
def request_client(tcp_client,kc_v,pkc,SK,id,client_text):
    print("新的线程处理客户请求：request_client")
    print("解密后报文类型为：", type(client_text), "报文内容为", client_text)
    # 对报文内容进行解密
    print(client_text)
    req_type = client_text.control_type
    sign = client_text.sign
    print("22222222222222222222222222222222222222222222222")
    print("请求为:",int(req_type),"用户类型为:",int(sign))
    if int(req_type)==5 and int(sign)==1:
        req_content = list(eval(client_text.content))
    elif int(req_type)==11 and int(sign)==2:
        req_content = list(eval(client_text.content))
    elif int(req_type)==7 and int(sign)==3:
        req_content = list(eval(client_text.content))
    else:
        req_content = dict(eval(client_text.content))
    print("22222222222222222222222222222222222222222222222")
    if sign == 1:
        request_user(tcp_client, kc_v, pkc, SK,id, req_type, req_content)
        print("客户")
    elif sign == 2:
        request_business(tcp_client, kc_v, pkc, SK,id, req_type, req_content)
        print("商家")
    elif sign == 3:
        server_deliver.request_deliver(tcp_client, kc_v, pkc, SK,id, req_type, req_content)
        print("骑手")
    else:
        print("用户类型失败")


def tuple_2_list(dict_info:tuple,results:tuple):
    results = list(results)
    results.insert(0, dict_info)
    return results
if __name__=='__main__':
    main()