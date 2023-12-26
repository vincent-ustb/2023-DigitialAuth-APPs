import sys
sys.path.append('C:/Users/blank/Desktop/kerberos-based-delivery-system-master/kerberos-based-delivery-system-master')

import packet
import pymysql
import server
import dictionary
import mysocket
import random
ack_flag=False
import time
import log

#相应客户登陆后的请求
def request_user(tcp_client,kc_v,pkc,SK,id,req_type:str,content:dict):
    """
    相应客户登陆后的请求
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 客户的id
    :param req_type: 请求类型
    :param content: 解密后的报文内容
    :return:
    """
    # #
    #   'ACK': '1001',

    #修改余额recharge:0011
    #change_money(tcp_client,id:str,passwd:str,money:int)
    print("````````````````````````````````````````响应客户请求1`````````````````````````````````")
    print("客户发送的请求为：",content,"请求类型为：",req_type)
    #客户充值金额recharge': '0011',///
    if int(req_type)==3:
        passwd=content["passwd"]
        money=int(content["money"])
        recharge(tcp_client,kc_v,pkc,SK,id,passwd,money)
    #查看订单详情''refresh':': '0100'//////////
    elif int(req_type)==4:
        refresh(tcp_client,kc_v,pkc,SK,id)
    #提交订单：submit:0101///////
    elif int(req_type)==5:
        submit_order(tcp_client,kc_v,pkc,SK,id,content)
    # 修改个人信息：'modify_info': '0111////////
    elif int(req_type)==7:
        print("客户要修改信息")
        name=content["name"]
        sex=content["sex"]
        address=content["address"]
        phonenumber=content["phonenumber"]
        cust_alter(tcp_client,kc_v,pkc,SK,id,name,sex,address,phonenumber)
    print("````````````````````````````````````````响应客户请求2`````````````````````````````````")



def __check_money(id_c):
    """
    客户端余额查询
    :param id:用户id
    """
    print("查询客户余额")
    sql="SELECT Cmoney FROM customer WHERE Cno='"+id_c+"'"
    print(sql)
    dict,rest_money=server.sql_select(sql)
    print("客户当前的余额为：",rest_money,"类型为:",type(rest_money))
    #查询余额
    return int(rest_money[0][0])
def cust_sign(tcp_client,id_c:str,password:str,name:str,sex:str,address:str,phonenumber:str,money:100):
    """
    用户注册
    :param id: 用户id
    :param password: 用户密码
    :param name: 用户名
    :param sex: 用户性别（M/F）
    :param address: 用户地址
    :param phonenumber: 用户电话
    :param money: 用户余额
    :return:
    """
    #添加用户信息
    #有内容为空
    log_txt="用户请求注册信息\n"
    flag=False
    if '' in [id_c,password,name,sex,address,phonenumber]:
        print("有内容为空，注册失败")
        log_txt += "有内容为空，注册失败\n"
        error_info = {"error_info": "有内容为空"};
        tcp_client.send(packet.get_pack("s_c", sign="user", control_type='signature',state="server_error", content=str(error_info)))
        log.debug(log_txt, path='./server_log/customer/', log_name=id_c + '.txt')
        return False
    exist_user_info=[]
    user_dict,resu=server.select("password")
    exist_usr_info=[]
    for row in resu:
        exist_usr_info.append(row[0])
    if id_c in exist_user_info:
        print("注册错误，用户id已存在")
        log_txt += "用户id已存在，注册失败\n"
        error_info = {"error_info": "用户id已存在"};
        tcp_client.send(packet.get_pack("s_c", sign="user", control_type='signature', state="server_error", content=str(error_info)))
    elif password==" "or id_c==" ":
        print("注册错误,id或密码为空")
        error_info = {"error_info": "id或密码为空"};
        tcp_client.send(packet.get_pack("s_c",sign="user", control_type='signature',state="server_error", content=str(error_info)))
    else:
        #将信息插入数据库

        ins = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{})'.format(id_c, password, name, sex, address, phonenumber, money)
        sql = "INSERT INTO customer VALUES " +ins
        print("注册sql语句为:",sql)
        server.sql_insert(sql)
        print('欢迎', '注册成功')
        log_txt += "欢迎，注册成功\n"
        tcp_client.send(packet.get_pack("s_c", control_type='signature',sign="user",state="success"))
        flag=True
    log.debug(log_txt, path='./server_log/customer/', log_name=id_c + '.txt')
    #判断是否添加成功
    #返回报文
    return flag
#修改信息
def cust_alter(tcp_client,kc_v,pkc,SK,id:str,name:str,sex:str,address:str,phonenumber:str):
    """
    客户修改信息
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 客户id：str
    :param name: 姓名：str
    :param sex: 性别：str
    :param address: 地址：str
    :param phonenumber: 电话：str
    :return: 返回修改信息是否正确
    """
    #判断密码是否正确
        #修改信息
    log_txt="用户要修改个人信息\n"
    print("````````````````````````````````````````客户要修改信息`````````````````````````````````")
    change=0
    sql_alt="UPDATE customer SET"
    modify_name=0
    modify_address=0
    modify_phonenumber=0
    modify_sex=0
        #名字不为空
    if name !="":
        sql_alt+=" Cname=\'"+ name+"\'"
        modify_name=1
        change=1
    #UPDATE customer SET Cpass='463c11fee9d44a34caa25b529da4fb6693573a0c42958cc5f5eaaacff94ca54a'
        #地址不为空
    if address!="":
        if change==1:
            sql_alt+=","
        sql_alt+=" Caddress=\'" + address + "\'"
        modify_address = 1
        change=1
        #电话号码
    if phonenumber!="":
        if change==1:
            sql_alt+=","
        sql_alt+=" Ctel=\'" + phonenumber + "\'"
        modify_phonenumber = 1
        change=1
    #性别
    if sex!="":
        if change==1:
            sql_alt+=","
        sql_alt+=" Csex=\'" + sex + "\'"
        modify_sex = 1
        change=1
    sql_alt+="WHERE Cno=\'"+id+"\';"
    print("sql语句为:",sql_alt)
    server.sql_insert(sql_alt)
    print("信息修改成功")

    dict_info = ('name', 'sex', 'address', 'phonenumber')
    flag=if_success_alter(modify_name, modify_sex, modify_address,modify_phonenumber, name,sex,address,phonenumber, id)
    if flag:
        print("信息修改成功")
        sql = "SELECT Cname,Csex,Caddress,Ctel FROM customer WHERE Cno='" + id + "'"
        print(sql)
        dict_info, results = server.sql_select(sql)
        print("用户当前信息为", results)
        log_txt+="用户当前信息为："+str(results[0])
        results = server.tuple_2_list(dict_info, results)
        print(results)
        log_txt += "用户个人信息修改成功\n"
        mypack = packet.get_pack("s_c", sign="user", state="success", control_type="modify_info", content=str(results),
                             sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag)
        print("报文发送成功")
        flag = True
    else:
        print("修改后信息不匹配")
        log_txt += "用户个人信息修改失败\n"
        mypack=packet.get_pack("s_c", sign="user", state="server_error",control_type="modify_info", content= "信息修改失败",sessionkey=kc_v,privatekey=SK)
        mysocket.send(tcp_client,mypack,ack_flag=ack_flag)
        flag=False
    print("````````````````````````````````````````客户修改信息结果，",flag,"`````````````````````````````````")
    log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
    return flag
def if_success_alter(name,sex,address,phonenumber, name1,sex1,address1,phonenumber1,id):
    print("修改信息为：",name1,sex1,address1,phonenumber1)
    print("修改值为：",name,sex,address,phonenumber)
    sql = "SELECT Cname,Csex,Caddress,Ctel FROM customer WHERE Cno='" + id + "'"
    print(sql)
    dict_info, results = server.sql_select(sql)
    print("用户当前信息为", results)
    print(name, sex, address, phonenumber)
    if (name==1 and name1==results[0][0]) or name==0:
        flag=True
    else:
        print("要修改的信息和修改后的信息不匹配1")
        return False
    if(sex==1 and sex1==results[0][1]) or sex==0:
        flag=True
    else:
        print("要修改的信息和修改后的信息不匹配2")
        return False
    if (address == 1 and address1 == results[0][2]) or address == 0:
        flag = True
    else:
        print("要修改的信息和修改后的信息不匹配3")
        return False
    if (phonenumber == 1 and phonenumber1 == results[0][3]) or phonenumber == 0:
        print("要修改的信息和修改后的信息匹配")
        return True
    else:
        print("要修改的信息和修改后的信息不匹配4")
        return False


#充值余额
def recharge(tcp_client,kc_v,pkc,SK,id:str,passwd:str,money:int):
    """
    用户充值余额
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param id: 用户id
    :param passwd: 用户密码
    :param money: 用户充值金额
    :return:
    """
    log_txt="客户充值余额\n充值金额为"+str(money)+"\n"
    print("````````````````````````````````````````客户要进行余额充值`````````````````````````````````")
    flag=server.__yanzheng(id,passwd,1)
    if flag:
        print(id, "充值余额验证成功")
        log_txt += "客户密码验证成功\n"
        if money == "" or int(money) <= 0:
            print("充值失败，余额输入不合法")
            log_txt+="客户充值失败，原因是余额输入不合法\n"
            mypack=packet.get_pack("s_c", sign="user",control_type='recharge',  state="server_error", content="余额输入不合法",sessionkey=kc_v,privatekey=SK)
            print(mypack)
            mysocket.send(tcp_client,mypack,sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
            log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
            flag = False
            return flag
        else:
            rest_money = __check_money(id)
            log_txt+="客户当前余额为:"+str(rest_money)
            target_money = int(money) + rest_money
            sql="UPDATE customer SET Cmoney="+str(target_money)+" WHERE Cno='"+id+"'"
            server.sql_insert(sql)
            print("充值成功,当前余额为", __check_money(id))
            log_txt+="\n客户充值成功，当前余额为"+str(__check_money(id))+"\n"
            mypack=packet.get_pack("s_c", sign="user",control_type='recharge', state="success", content=str(target_money),sessionkey=kc_v,privatekey=SK)
            print(mypack)
            mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
            log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
            flag = True
    else:
        print("用户id密码不匹配")
        log_txt+="用户充值失败，id和密码不匹配\n"
        mypack = packet.get_pack("s_c", sign="user", control_type='recharge', state="server_error", content="id和密码不匹配",sessionkey=kc_v,privatekey=SK)
        print(mypack)
        mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc,  ack_flag=ack_flag)
        flag=False
    print("````````````````````````````````````````客户余额充值结束，结果为",flag,"`````````````````````````````````")
    log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
    return flag



#查看商品信息
def __get_menu():
    """
    客户端查询当前开店的店铺及菜单信息
    :return:
    """
    print("````````````````````````````````````````客户要查看商品信息`````````````````````````````````")
    flag=True
    sql="SELECT store.Sno,goods.Gno,store.Sname,goods.Gname,goods.Gprice FROM store,goods WHERE store.Sno=goods.Sno AND store.Sstate='工作'"
    dict_info, results = server.sql_select(sql)
    if len(results)==0:
        return 0
    else:
        dict_info=('商店id','食品id','商店名称','食物名称','食物价格')
        results=server.tuple_2_list(dict_info,results)
        print(results)
        return results
    #给客户返回菜品信息
    # mypack=packet.get_pack('s_c',sign='user',control_type='get_menu',state='success',content=results,sessionkey=kc_v,privatekey=SK)
    # mysocket.send(tcp_client, mypack, ack_flag=ack_flag)
    # print("````````````````````````````````````````商品信息已发送给客户`````````````````````````````````")

#查看订单信息//////////order_details
def __check_order_info(id):
    """
    查看订单信息，发送订单id，商家名称，金额，状态，日期
    :param tcp_client:
    :param kc_v:
    :param pkc:
    :param SK:
    :param id:
    :return:
    """
    print("客户",id,"要查询订单信息")
    sql="SELECT orderr.Ono,store.Sname,orderr.Omoney,orderr.Ostate,orderr.Obtime FROM orderr,store WHERE orderr.Sno=store.Sno AND orderr.Cno='"+id+"' order by orderr.Obtime desc"
    print(sql)
    dict,results=server.sql_select(sql)
    if len(results) > 0:
        dict_info = ("订单id", "商家名称", "金额", "订单状态", "日期")
        results = server.tuple_2_list(dict_info, results)
        return results
    else: return 0

def __check_cust_info(id):

    print("客户",id,"要查询个人信息")
    sql="SELECT Cno,Cname,Csex,Caddress,Ctel,Cmoney FROM customer WHERE Cno='"+id+"'"
    print(sql)
    dict,results=server.sql_select(sql)
    dict=("id","姓名","性别","地址","电话号码","余额")
    result=server.tuple_2_list(dict,results)
    print(type(results))
    return result
def refresh(tcp_client,kc_v,pkc,SK,id):
    """

    :param tcp_client:
    :param kc_v:
    :param pkc:
    :param SK:
    :return:
    """
    a=[]
    log_txt="用户刷新信息\n"
    print("客户需要刷新信息")
    #客户信息
    content1=__check_cust_info(id)
    # print("客户信息为：",content1)
    log_txt+="用户个人信息为:"+str(content1)+"\n"
    a.append(list(content1))
    #商品信息
    content2=__get_menu()
    # log_txt += "菜单信息为:" + str(content2)+"\n"
    #订单信息
    content3=__check_order_info(id)
    log_txt += "订单信息为:" + str(content3) + "\n"
    # print("content1type为：",type(content1),"content2type为：",type(content2),"content3type为：",type(content3))
    if (str(content2)!=str(0)):
        a.append(content2)
    if (str(content3)!=str(0)):
        a.append(list(content3))
    print(type(content2),type(content2))
    if (str(content3)=='0') and (str(content2)==str(0)):
        state='c'
    elif (str(content3)!=str(0) )and (str(content2)!=str(0)):
        state='success'
    elif (str(content2)=='0') and (str(content3)!=str(0)):
        state='a'
    elif (str(content2)!='0') and (str(content3)==str(0)):
        state="b"
    print("state为：",state )
    print("刷新时发送的内容为:",str(a))
    mypack=packet.get_pack('s_c', sign='user', control_type='refresh', state=state, content=str(a), sessionkey=kc_v, privatekey=SK)
    mysocket.send(tcp_client,mypack,sessionkey=kc_v, publickey=pkc,ack_flag=ack_flag)
    print("刷新报文发送成功")
    log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')

#获取当前时间
def __get_time():
    t=time.time()
    timeArray=time.localtime(t)
    time_str=time.strftime('%Y-%m-%d %H:%M:%S',timeArray)
    print(type(time_str),time_str)
    return time_str
#计算订单总额
#客户id，商家id，菜品id
def __sum_money(content:str):
    print("开始计算订单总额")
    content=str(content)
    XX = list(eval(content))
    money=0
    for i in range(len(XX)):
        sql="SELECT Gprice FROM goods,store WHERE goods.Gno='"+str(XX[i][1])+"' AND goods.Sno='"+str(XX[i][0])+"' AND goods.Sno=store.Sno"
        print(sql)
        dict,results=server.sql_select(sql)
        money+=results[0][0]
    print("总金额为",money)
    return int(money)
#提交订单//////
def submit_order(tcp_client,kc_v,pkc,SK,id,content:str):
    """
    用户提交订单，用户余额进行相应修改
    :param tcp_client: socket
    :param kc_v: sessionkey
    :param pkc: C的公钥
    :param SK: V的私钥
    :param content: 报文内容
    :return:
    """
    log_txt="用户提交订单\n"
    print("`````````````````````````````开始提交订单······································")
    print("传入的content的类型为:",type(content),"内容为:",content)
    # print(content)
    content = str(content)
    log_txt+="用户提交的商家，食品id为:"+str(content)+"\n"
    # 商家营业额增加，库存降低
    # mypack=packet.get_pack('s_c',sign='user',control_type='get_menu',state='success',content=results,sessionkey=kc_v,privatekey=SK)
    # mysocket.send(tcp_client, mypack, ack_flag=ack_flag)
    #提交订单，计算金额
    sum_money=__sum_money(content)
    log_txt += "用户提交的订单总额为:" + str(sum_money) + "\n"
    #查询客户余额
    recent_money=int(__check_money(id))
    log_txt += "用户的余额为:" + str(recent_money) + "\n"
    if sum_money>recent_money:
        # print("当前客户的余额不足")
        log_txt += "用户的余额不足,订单提交失败\n"
        mypack=packet.get_pack('s_c',sign='user',control_type='submit_order',state='server_error',content="余额不足",sessionkey=kc_v,privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
        log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
        return False
        #向客户发送商品库存不足的信息
    #客户余额减少，余额不足返回错误

    else:
        content = list(eval(content))
        a = []
        for row in content:
            if row[0] in a:
                continue;
            else:
                a.append(row[0])
        # print("客户余额可以支付订单费用")
        log_txt += "用户的余额足以支付订单费用\n"
        #客户余额减少
        sql="UPDATE customer SET Cmoney="+str(recent_money-sum_money)+""
        print(sql)
        server.sql_insert(sql)
        # print("content的类型为",type(content),"内容为：",content)
        # print("当前商家为：",a,"有",len(a),"家商家")
        for i in range(len(a)):
            # print("················第", i, "个商家··································")
            goods = []
            # print("当前商家为：", a[i])
            for row in content:
                # print("商家id row[0]=",row[0],"菜品id row[1]=",row[1])
                if row[0] == a[i]:
                    goods.append(row[1])
            # print("订单中", a[i], "家的食物为:", goods)
            store_id = a[i]
            order_money = 0
            for j in range(len(goods)):
                good_id = goods[j]
                sql = "SELECT Gno,Gname,Gprice,Gstock FROM store,goods WHERE store.Sno=Goods.Sno AND store.Sno='" + store_id + "' AND goods.Gno='" + good_id + "'"
                dict, results = server.sql_select(sql)
                # print(sql, "查询的结果为：", results)
                Gno = results[0][0]
                Gname = results[0][1]
                Gprice = results[0][2]
                Gstock = results[0][3]
                Gno = results[0][0]
                order_money += Gprice
                # 库存-1
                sql = "UPDATE goods SET Gstock=" + str(Gstock - 1) + " WHERE Gno='" + Gno + "'"
                server.sql_insert(sql)
                # 查询更新后的库存
                sql1 = "SELECT Gstock From goods WHERE goods.Gno='" + Gno + "'"
                dict, se_results = server.sql_select(sql1)
                # print("之前", Gname, "的库存为", Gstock, "    ", sql, " 执行后的结果为:", se_results[0][0])
            # 商家营业额增加
            # 查询当前商家的营业额

            sql = "SELECT Smoney FROM store WHERE Sno='" + store_id + "'"
            print(sql)
            dict, results = server.sql_select(sql)
            old_money = results[0][0]
            print("此订单的金额为：", order_money)
            print("商家之前的营业额为:", old_money)
            new_money = old_money + order_money
            print("商家当前的营业额为:", new_money)
            sql = "UPDATE store SET Smoney=" + str(new_money) + " WHERE Sno='" + store_id + "'"
            # print(sql)
            server.sql_insert(sql)
            sql = "SELECT Smoney FROM store WHERE Sno='" + store_id + "'"
            # print(sql)
            dict, results = server.sql_select(sql)
            new_money = results[0][0]
            print("商家现在的营业额为:", new_money)
            # 分配骑手
            sql = "SELECT Count(*) FROM deliverer WHERE Dstate='工作'"
            dict1, results1 = server.sql_select(sql)
            # print(results1[0][0])
            count = random.randint(0, int(results1[0][0]) - 1)
            # 查找出所有正在工作的骑手的id
            sql = "SELECT Dno FROM deliverer WHERE Dstate='工作'"
            dict, results = server.sql_select(sql)
            # print(results)
            # 选择第count个骑手进行派单
            deliver_id = results[count][0]
            # 查询当前订单编号的最大值
            sql = "SELECT MAX(Ono+0) FROM orderr"
            dict, results = server.sql_select(sql)
            # print("当前订单最大值为:", results[0][0])
            order_id = int(results[0][0]) + 1
            # 获得当前的时间
            order_time = __get_time()
            # 更新orderr表(#订单id，骑手id，客户id，商家id，状态，提示Otip,配送费，金额，时间)
            # sql="INSERT INTO orderr VALUES("+'(\'{}\',{},\'{}\',{},\'{}\',\'{}\',\'{}\',\'{}\',{})' \
            #     .format(str(order_id), deliver_id, id,, '正在出餐', '无', '5', 5, )
            sql = "INSERT INTO orderr VALUES(" + '\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{},{},\'{}\')'.format(
                str(order_id), deliver_id, id, store_id, '正在出餐', '无', '5', order_money, order_time)
            # print(sql)
            server.sql_insert(sql)
            # 更新purchase表
            for j in range(len(goods)):
                good_id = goods[j]
                sql = "INSERT INTO purchase VALUES(" + '\'{}\',\'{}\',{})'.format(str(order_id), good_id, 1)
                # print(sql)
                server.sql_insert(sql)
            # print("················第", i, "个商家结束··································")

        mypack = packet.get_pack('s_c', sign='user', control_type='submit', state='success',sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
        log_txt += "订单提交成功\n"
        log.debug(log_txt, path='./server_log/customer/', log_name=id + '.txt')
        return True

        #随机选择外卖员（正在上班的）进行派送
