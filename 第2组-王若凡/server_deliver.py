import pymysql
# from server import *
import packet
import server
import mysocket
import log

ack_flag=False
def deli_sign(tcp_client,id_c:str,password:str,name:str,sex:str,phonenumber:str,money:int,state='休息'):
    """
    骑手注册
    :param tcp_client:socket
    :param id_c:骑手id
    :param password:骑手密码
    :param name:骑手姓名
    :param sex:性别
    :param phonenumber:电话号码
    :param money:骑手工资：初始为0
    :param state:骑手状态：初始为休息
    :return:
    """
    #添加用户信息
    #有内容为空
    flag=False
    log_txt="骑手开始注册了"
    print("开始注册")
    if '' in [id_c,password,name,sex,phonenumber]:
       print("有内容为空，注册失败")
       log_txt+= "\n骑手注册失败，原因是有内容为空"
       tcp_client.send(packet.get_pack("s_c", sign="deliver",state="server_error", content= "有内容为空"))
    exist_user_info=[]
    sql="SELECT Dno FROM deliverer"
    dict,results=server.sql_select(sql)
    for row in results:
        exist_user_info.append(row[0])
    flag=True
    if id_c in exist_user_info:
        log_txt += "\n骑手注册失败，原因是id已存在"
        print("注册错误，用户id已存在")
        tcp_client.send(packet.get_pack("s_c", sign="deliver", state="server_error", content="用户id已存在"))
        flag = False
    if flag:
             #将信息插入数据库
        ins = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{},\'{}\')'.format(id_c, password, name, sex, phonenumber, money,state)
        sql = "INSERT INTO deliverer VALUES " + ins
        print("注册sql语句为:", sql)
        server.sql_insert(sql)
        log_txt += "\n骑手注册成功"
        print('欢迎骑手', id, '注册成功')
        tcp_client.send(packet.get_pack("s_c", control_type="signature",sign="deliver", state="success"))
        flag = True
    log.debug(log_txt, path='./server_log/deliver/', log_name=id_c + '.txt')
    #判断是否添加成功
    #返回报文
    return flag
def request_deliver(tcp_client, kc_v, pkc, SK, id:str,req_type:str,content:dict):
    """
    骑手请求响应端
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: publickey
    :param SK: privatekey
    :param req_type: 请求状态
    :param req_content: 请求报文内容
    :return:
    """
    # log_txt=""
    # log.debug(log_txt, path='./server_log/', log_name=id + '.txt')
    print("骑手进行响应,请求类型为：", int(req_type))

    # 修改个人信息:modify_info:0100/////////
    if int(req_type) == 4:
        # log_txt += "骑手发出修改信息的请求\n"
        # id = content["id"]
        name = content["name"]
        sex = content["sex"]
        phonenumber = content["phonenumber"]
        modify_info(tcp_client, kc_v, pkc, SK, id, name, sex,phonenumber)
    # 提现'cash_out': '0101'//////
    elif int(req_type) == 5:
        # id=content["id"]
        print("客户要提现,content为:",type(content),content)
        passwd=content["passwd"]
        print(passwd)
        money=int(content["money"])
        print(money)
        cash_out(tcp_client, kc_v, pkc, SK, id,passwd,money)
    # 完成订单：'finish_order': '0111'/////////
    # 发送list
    elif int(req_type) == 7:
        print("请求为提交订单,content_type为",type(content))
        # d_id=content["id"]
        #o_id=content["id_o"]
        finish_order(tcp_client, kc_v, pkc, SK, id,content)
    #  刷新代配送订单 'refresh': '1000',
    elif int(req_type) == 8:
        refresh(tcp_client, kc_v, pkc, SK, id)
    # 一键上下班: 'one_click_commuting': '1001',/////
    elif int(req_type) == 9:
        # id = content["id"]
        one_click_commuting(tcp_client, kc_v, pkc, SK, id)
    return 0

def __check_order_left(id):
    #店铺，收货人地址，收货人电话，配送费
    print("````````````````````````````````````````骑手要查看待配送订单信息信息`````````````````````````````````")
    flag = True
    sql = "SELECT store.Sname,customer.Caddress,customer.Ctel,orderr.ODelfee,orderr.Ono FROM orderr,customer,store WHERE customer.Cno=orderr.Cno AND store.Sno=orderr.Sno AND orderr.Dno='"+id+"' AND orderr.Ostate='正在配送'"
    print(sql)
    dict_info, results = server.sql_select(sql)
    if len(results) == 0:
        return 0
    else:
        dict_info = ('店铺名称', '收货人地址', '收货人电话', '配送费','订单id')
        results = server.tuple_2_list(dict_info, results)
        print(results)
        return results

#
def __check_order_right(id):
    #订单号，商家名，金额，状态，时间
    print("````````````````````````````````````````骑手要查看最近订单信息`````````````````````````````````")
    flag = True
    sql = "SELECT orderr.Ono,store.Sname,orderr.Omoney,orderr.Ostate,orderr.OBtime FROM orderr,store WHERE store.Sno=orderr.Sno AND orderr.Dno='"+id+"' order by orderr.OBtime desc limit 0,10"
    print(sql)
    dict_info, results = server.sql_select(sql)
    if len(results) == 0:
        return 0
    else:
        dict_info = ('订单号', '商家名', '金额', '状态',"时间")
        results = server.tuple_2_list(dict_info, results)
        print(results)
        return results
def __check_deliver_info(id):
    print("客户",id,"要查询个人信息")
    sql="SELECT Dno,Dname,Dsex,Dtel,Dmoney,Dstate FROM deliverer WHERE Dno='"+id+"'"
    print(sql)
    dict,results=server.sql_select(sql)
    dict=("id","姓名","性别","电话号码","工资","状态")
    result=server.tuple_2_list(dict,results)
    print(type(results))
    return result
#刷新
def refresh(tcp_client, kc_v, pkc, SK, id):
    log_txt="骑手提出刷新信息的请求"
    a=[]
    print("骑手刷新信息")
    content1=__check_deliver_info(id)
    log_txt+="\n骑手个人信息为："+str(content1)
    # print("骑手个人信息为",content1)
    a.append(content1)
    content2=__check_order_left(id)
    # print("\n骑手待配送订单为：", content2)
    log_txt += "骑手个人信息为：" + str(content2)
    content3=__check_order_right(id)
    # print("骑手个人信息为", content3)
    log_txt += "骑手最近订单为：" + str(content3)
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
    mypack = packet.get_pack('s_c', sign='deliver', control_type='refresh', state=state, content=str(a), sessionkey=kc_v,
                             privatekey=SK)
    mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    print("刷新报文发送成功")
    log_txt+="\n刷新请求完成"
    log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')
    return 0


def __if_success_alter(modify_name,modify_sex,modify_phonenumber,name,sex,phonenumber,id):
    print("修改信息为：", name, sex, phonenumber)
    print("修改值为：", modify_name,modify_sex, modify_phonenumber)
    sql = "SELECT Dname,Dsex,Dtel FROM deliverer WHERE Dno='" + id + "'"
    print(sql)
    dict_info, results = server.sql_select(sql)
    print("用户当前信息为：", results[0][0],results[0][1],results[0][2])
    print("用户要修改的信息为：",name, sex, phonenumber)
    print("修改值为：",modify_name,modify_sex, modify_phonenumber)
    if (modify_name == 1 and name == results[0][0]) or modify_name == 0:
        print("姓名修改匹配")
        flag = True
    else:
        print("要修改的信息和修改后的信息不匹配1")
        return False
    if (modify_sex == 1 and sex == results[0][1]) or modify_sex == 0:
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
#修改信息
def modify_info(tcp_client, kc_v, pkc, SK, id:str,name:str,sex:str,phonenumber:str):
    """
    修改外卖员的信息
    :param tcp_client:socket
    :param kc_v: sessionkey
    :param pkc: publickey
    :param SK: privatekey
    :param id: id
    :param name: name
    :param sex: sex
    :param phonenumber: 电话号码
    :return:
    """
    # 修改信息
    log_txt=''
    log_txt += "骑手发出修改信息的请求\n骑手发送的信息为:"
    log_txt+=str(name)+str(sex)+str(phonenumber)
    modify_name = 0
    modify_sex = 0
    modify_phonenumber = 0
    change = 0
    sql_alt = "UPDATE deliverer SET"
    # 名字不为空
    if name != "":
        sql_alt += " Dname=\'" + name + "\'"
        modify_name = 1
        change = 1
    # UPDATE customer SET Cpass='463c11fee9d44a34caa25b529da4fb6693573a0c42958cc5f5eaaacff94ca54a'
    # 性别不为空
    if sex != "":
        if change == 1:
            sql_alt += ","
        sql_alt += " Dsex=\'" + sex+ "\'"
        modify_sex =1
        change = 1
    # 电话号码
    if phonenumber != "":
        if change == 1:
            sql_alt += ","
        sql_alt += " Dtel=\'" + phonenumber + "\'"
        modify_phonenumber=1
        change = 1

    sql_alt += "WHERE Dno=\'" + id + "\';"
    print("sql语句为:", sql_alt)
    server.sql_insert(sql_alt)
    print("信息修改成功")
    flag=__if_success_alter(modify_name,modify_sex,modify_phonenumber,name,sex,phonenumber,id)
    if flag:
        log_txt += "骑手修改信息成功\n"
        sql_recent = "SELECT Dname,Dsex,Dtel FROM deliverer WHERE Dno='" + id + "'"
        print(sql_recent)
        dict_info, resutls_recent = server.sql_select(sql_recent)
        content = {"name": resutls_recent[0][0], "sex": resutls_recent[0][1], "phonernumber": resutls_recent[0][2]}
        print("修改后的信息为:", id, "   ", content)
        log_txt+="骑手修改后的信息为"
        log_txt+=str(content)
        mypack=packet.get_pack("s_c", sign="deliver", control_type='modify_info', state="success", content=str(content),
                            sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client,mypack,ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
        flag = True

    else:
        log_txt += "骑手修改信息失败"
        mypack=packet.get_pack("s_c", sign="deliver", control_type='modify_info', state="success", content="信息修改失败",
                            sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client,mypack,ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
        flag = False
    alter_info_dict, alter_pre_info = server.select("deliverer", 'WHERE Dno=' + id)
    info = alter_pre_info[0]
    print("用户当前信息为", info)
    log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')
    return flag
def cash_out(tcp_client,kc_v,pkc,SK,id:str,passwd:str,money:int):
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
    log_txt="骑手发出提现请求，提现金额为"+str(money)+"\n"
    flag=server.__yanzheng(id,passwd,3)
    if flag:
        print("骑手",id,"要提现",str(money))
        sql_cash_out="SELECT Dmoney FROM deliverer WHERE Dno='"+id+"'"
        dict_info,result=server.sql_select(sql_cash_out)
        print(result)
        if money<=0:
            print("输入有误")
            error_info="金额输入不合法"
            log_txt+="骑手输入的金额小于等于0，不合法\n"
            mypack=packet.get_pack("s_c", sign="deliver",control_type='cash_out' ,state="server_error", content=str(error_info),sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client,mypack,ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
            return False
        print(type(money),money,type(result[0][0]),result[0][0])
        if result[0][0]>=money:
            print("够提现")

            sql_cash_update="UPDATE deliverer SET Dmoney="+str(result[0][0]-money)+" WHERE Dno='"+id+"'"
            server.sql_insert(sql_cash_update)
            sql_cash_out = "SELECT Dmoney FROM deliverer WHERE Dno='" + id + "'"
            print(sql_cash_out)
            dict_info, result1 = server.sql_select(sql_cash_out)
            if result1[0][0]==result[0][0]-money:
                print("余额更新成功")
                log_txt += "骑手提现成功\n"
                details=result1[0][0]
                mypack=packet.get_pack("s_c", sign="deliver",control_type='cash_out', state="success",content=str(details),sessionkey=kc_v, privatekey=SK)
                mysocket.send(tcp_client,mypack,sessionkey=kc_v,publickey=pkc,ack_flag=ack_flag)
                return True
            else:
                print("提现失败")
                log_txt += str("骑手提现失败\n")
                mypack = packet.get_pack("s_c", sign="deliver",control_type='cash_out', state="server_error", content="提现失败",
                                     sessionkey=kc_v, privatekey=SK)
                mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
        else:
            print("提现金额超过余额")
            log_txt += "骑手提现金额大于余额\n"
            mypack = packet.get_pack("s_c", sign="deliver",control_type='cash_out', state="server_error", content="提现失败",
                                     sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack,sessionkey=kc_v,publickey=pkc,ack_flag=ack_flag)
    else:
        print("密码输入有误")
        log_txt+="骑手密码输入有误\n"
        mypack = packet.get_pack("s_c", sign="deliver", control_type='cash_out', state="server_error",
                                 content= "密码输入有误",
                                 sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
    log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')

def one_click_commuting(tcp_client,kc_v,pkc,SK,id:str):
    """
        一键切换上下班
        :param tcp_client:socket
        :param kc_v: sessionkey
        :param pkc: C的公钥
        :param SK: V的私钥
        :param id: 骑手id：str
        :return:
        """
    log_txt="骑手提出一键上下班请求\n"
    sql = "SELECT Dstate FROM deliverer WHERE Dno='" + id + "'"
    print("切换上下班执行的sql语句为：", sql)
    data_dict, results1 = server.sql_select(sql)
    print(results1)
    if results1[0][0] == '休息':
        print("当前骑手在休息")
        log_txt += "当前骑手在休息\n"
        sql = "UPDATE deliverer SET Dstate='工作' WHERE Dno='" + id + "'"
        server.sql_insert(sql)
    else:
        print("当前骑手在工作")
        log_txt += "当前骑手在工作\n"
        sql = "UPDATE deliverer SET Dstate='休息' WHERE Dno='" + id + "'"
        server.sql_insert(sql)
    sql = "SELECT Dstate FROM deliverer WHERE Dno='" + id + "'"
    data_dict, results = server.sql_select(sql)
    detail="骑手"+id,results[0][0]+ "了"
    log_txt += str(detail)
    # 发送报文
    # 报文内容
    if results[0][0] != results1[0][0]:
        log_txt += "骑手一键上下班成功"
        mypack = packet.get_pack("s_c", sign="deliver", control_type='one_click_commuting', state="success",
                                 content=str(results[0][0]), sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
    else:
        log_txt += "骑手一键上下班失败"
        mypack = packet.get_pack("s_c", sign="deliver", control_type='one_click_commuting', state="server_error",
                                 content=str("修改状态失败"), sessionkey=kc_v, privatekey=SK)
        mysocket.send(tcp_client, mypack, ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
    log.debug(log_txt, path='./server_log/deliver/', log_name=id + '.txt')
def finish_order(tcp_client, kc_v, pkc, SK, d_id:str,content:list):
    """
    骑手完成订单，骑手工资加10，订单状态改为已送达
    :param tcp_client:
    :param kc_v:
    :param pkc:
    :param SK:
    :param d_id:
    :param o_id:
    :return:
    """
    #判断骑手发送的id是否合法
    log_txt="骑手发送完成订单请求，订单id为:"+str(content)+"\n"
    for i in range(len(content)):
        o_id=content[i]
        print("````````````````````骑手完成订单1``````````````````````````````````````````````````````")
        sql = "SELECT Ostate FROM orderr WHERE Dno='" + d_id + "' AND Ono='" + o_id + "'"
        print(sql)
        dict_info,results=server.sql_select(sql)
        if len(results)==0:
            print("订单号错误")
            error_info = "订单号错误"
            log_txt+="订单号有误"
            mypack = packet.get_pack("s_c", sign="deliver", control_type='finish_order', state="server_error",
                                 content=str(error_info), sessionkey=kc_v, privatekey=SK)
            mysocket.send(tcp_client, mypack,sessionkey=kc_v, publickey=pkc, ack_flag=ack_flag)
            log_txt += "完成订单失败"
            log.debug(log_txt, path='./server_log/deliver/', log_name=d_id + '.txt')
            return False
        else:
        #将此订单的状态改为已修改
            sql="UPDATE orderr SET Ostate='订单完成' WHERE Ono='"+o_id+"'"
            # print("修改信息的sql语句为：",sql)
            server.sql_insert(sql)
        #查看修改后的状态
            sql = "SELECT Ostate FROM orderr WHERE Dno='" + d_id + "' AND Ono='" + o_id + "'"
            # print(sql)
            dict_info, results = server.sql_select(sql)
            # print("修改后的状态为",results)

        #骑手工资+20
        #查看骑手当前工资
            sql="SELECT Dmoney FROM deliverer WHERE Dno='"+d_id+"'"
            # print("查看骑手工资的sql语句为：",sql)
            dict_info,results=server.sql_select(sql)
            # prisongfei
            sql = "SELECT Count(*) FROM purchase WHERE Ono='" + o_id + "'"
            dict, peisongfei = server.sql_select(sql)
            peisongfei=int(peisongfei[0][0])*2
            new_salary=results[0][0]+peisongfei
            sql="UPDATE deliverer SET Dmoney="+str(new_salary)+" WHERE Dno='"+d_id+"'"
            # print("骑手工资增加五的sql语句为:",sql)
            server.sql_insert(sql)
            sql = "UPDATE orderr SET Ostate='订单完成' WHERE Ono='" + o_id + "'"
            # print("订单状态发生变化的sql语句为:", sql)
            server.sql_insert(sql)
            sql = "SELECT Dmoney FROM deliverer WHERE Dno='" + d_id + "'"
            # print("查看骑手工资的sql语句为：", sql)
            dict_info, results = server.sql_select(sql)
            if results[0][0]==new_salary:
                #发送订单完成成功报文
                print("订单",i,"完成")
                log_txt += "骑手当前工资为"+str(new_salary)
                log_txt+="\n订单完成"
                flag=True
                # mypack = packet.get_pack("s_c", sign="deliver", control_type='finish_order', state="success",
                #                      content=str(new_salary), sessionkey=kc_v, privatekey=SK)
                # mysocket.send(tcp_client, mypack)
            #发送报文
            else:
                flag=False
                error_info = "骑手工资未修改成功"
                log_txt += "\n骑手工资修改失败"
                mypack = packet.get_pack("s_c", sign="deliver", control_type='finish_order', state="server_error",
                                     content=str(error_info), sessionkey=kc_v, privatekey=SK)
                mysocket.send(tcp_client, mypack,ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
                log.debug(log_txt, path='./server_log/deliver/', log_name=d_id + '.txt')
                return False
    print("````````````````````骑手完成订单2``````````````````````````````````````````````````````")
    mypack = packet.get_pack("s_c", sign="deliver", control_type='finish_order', state="success",
                          content=str(new_salary), sessionkey=kc_v, privatekey=SK)
    mysocket.send(tcp_client, mypack,ack_flag=ack_flag,sessionkey=kc_v, publickey=pkc)
    print("完成订单报文发送成功")
    log_txt=str(log_txt)

    log.debug(log_txt, path='./server_log/deliver/', log_name=(str(d_id) + '.txt'))
    return flag
