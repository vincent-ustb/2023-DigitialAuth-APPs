import time
import datetime

pac_type = {'c_a': '0001', 'a_c': '0010', 'c_t': '0011', 't_c': '0100', 'c_s': '0101', 's_c': '0110'}

sign = {'none': '0000', 'user': '0001', 'business': '0010', 'deliver': '0011'}

state = {'none': '0000', 'success': '0001', 'client_error': '0010', 'server_error': '0011',"a":"0100","b":"0101","c":"0110","d":"0111","e":"1000"}

ack = {'NO': '00', 'YES': '01'}

code_type = {'ASCII': '0001', 'GBK': '0010', 'Unicode': '0011', 'utf-8': '0100'}

# 因为pac_type不同对应的control_type值有重复，因此将每个pac_type对应的control_type分开
# ticket1为票据许可票据 ticket2为服务许可票据
# type分别与pac_type与sign结合的顺序一一对应
# 文档中server发给不同client好像忘了写
# 后续删除0b且全打''
control_type1 = {'get_ticket1': '0001', 'request_enroll': '0010', 'modify_pwd': '0011', 'unknown1': '0100'}

control_type2 = {'return_ticket1': '0001', 'ACK': '0010', 'unknown1': '0011', 'unknown2': '0100'}

control_type3 = {'request_ticket2': '0001', 'unknown1': '0010', 'unknown2': '0011'}

control_type4 = {'return_ticket2': '0001', 'unknown1': '0010', 'unknown2': '0011'}

# message5认证.order_details是订单详情（订单里又什么信息），order_state是订单状态：时间，当前状态等信息
# recharge:充值
control_type5 = {'message5': '0001', 'signature': '0010', 'recharge': '0011','refresh': '0100',
                 'submit': '0101', 'modify_info': '0111','ACK': '1001', 'modify_pwd': '1010','unknown2': '1011', 'unknown3': '1100'}
# control_type6：对一些功能请求进行了修改
control_type6 = {'message5': '0001', 'signature': '0010', 'modify_pwd': '0011', 'modify_info': '0100',
                 'one_click_commuting': '0101', 'refresh_order': '0110', 'product_details': '0111',
                 'modify_product': '1000',
                 'new_product': '1001', 'delete_product': '1010', 'finish_order': '1011', 'cash_out': '1100',
                 'unknown1': '1101',
                 'unknown2': '1110', 'unknown3': '1111'}
#type7是骑手
# control_type:order_to_dlv:刷新代配送订单功能
control_type7 = {'message5': '0001', 'signature': '0010', 'modify_pwd': '0011', 'modify_info': '0100', 'cash_out': '0101',
                 'search_order': '0110', 'finish_order': '0111', 'refresh': '1000', 'one_click_commuting': '1001',
                 'unknown2': '1010'}

# 分别是s-c1 ，s-c2， s-c3
# control_type8 = {'message6': '0001', 'respond_add_cart': '0010', 'respond_recharge': '0011',
#                  'respond_product_details': '0100', 'respond_submit': '0101', 'respond_order_details': '0110',
#                  'respond_modify': '0111', 'respond_get_menu': '1000', 'ACK': '1001', 'unknown1': '1010',
#                  'unknown2': '1011', 'unknown3': '1100'}

control_type8 = {'message5': '0001', 'signature': '0010', 'recharge': '0011',
                 'refresh': '0100', 'submit': '0101', 'modify_info': '0111','ACK': '1001', 'modify_pwd': '1010','unknown2': '1011', 'unknown3': '1100'}
# control_type9 = {'respond_product_details': '0001', 'respond_order_details': '0010', 'respond_work': '0011',
#                  'respond_get_off': '0100', 'respond_modify_product': '0101', 'respond_new_product': '0110',
#                  'respond_delete_product': '0111', 'respond_search_order': '1000', 'respond_finish_order': '1001',
#                  'respond_modify': '1010', 'unknown1': '1011', 'unknown2': '1100', 'unknown3': '1101',
#                  'unknown4': '1110', 'unknown5': '1111'}
control_type9 = {'message5': '0001', 'signature': '0010', 'modify_pwd': '0011', 'modify_info': '0100',
                 'one_click_commuting': '0101', 'refresh_order': '0110', 'product_details': '0111',
                 'modify_product': '1000',
                 'new_product': '1001', 'delete_product': '1010', 'finish_order': '1011', 'cash_out': '1100',
                 'unknown1': '1101',
                 'unknown2': '1110', 'unknown3': '1111'}
# control_type10 = {'respond_modify': '0001', 'respond_work': '0010', 'respond_get_off': '0100', 'respond_salary': '0101',
#                   'respond_search_order': '0110', 'respond_finish_order': '0111', 'unknown1': '1000',
#                   'unknown2': '1001', 'unknown3': '1010'}
control_type10 = {'message5': '0001', 'signature': '0010', 'modify_pwd': '0011', 'modify_info': '0100',
                  'cash_out': '0101','search_order': '0110', 'finish_order': '0111', 'refresh': '1000', 'one_click_commuting': '1001',
                  'unknown2': '1010'}

"""下面是kerberos交互全过程中，所有报文的数据段的格式，使用时只需要填充对应的字段即可"""
# 注意深浅拷贝！
# lifetime单位是min， 默认为8h即480min
# ts格式为"%Y-%m-%d %H:%M:%S"
message1 = {"idc": "", "id_tgs": "", "ts1": "2022-05-11 01:33:15"}
message2 = {"kc_tgs": "", "id_tgs": "", "ts_2": "", "lifetime": "480", "tgt": ""}
message3 = {"idv": "", "tgt": "", "Authenticator_c": ""}
message4 = {"kc_v": "", "idv": "", "ts_4": "", "ticket": "", "private_key": ""}

message5 = {"ticket": "", "Authenticator_c": ""}
message6 = {"pk_v": "", "ts6": ""}

tgt = {"kc_tgs": "", "id_c": "", "ad_c": "", "id_tgs": "", "ts_2": "", "lifetime_2": "480"}
ticket = {"kc_v": "", "id_c": "", "ad_c": "", "id_v": "", "ts_4": "", "lifetime_4": "480", 'publickey': ''}
Authenticator_c = {"id_c": "", "ad_c": "", "ts_5": ""}


# certificate = {'version': 'v3','serial_num': '','user_id': '','src_time': '','end_tiem': '','publickey': '',}

# 根据ts时间判断是否存在消息重放
def compare_time():
    # timestamp = int(message1['ts1'], 2)
    timenow = int(time.time())
    src_time = message1['ts1']
    now_time = datetime.datetime.utcfromtimestamp(timenow).strftime("%Y-%m-%d %H:%M:%S")
    src_datetime = datetime.datetime.strptime(src_time, "%Y-%m-%d %H:%M:%S")
    now_datetime = datetime.datetime.strptime(now_time, "%Y-%m-%d %H:%M:%S")
    if (now_datetime - src_datetime).seconds > 60:
        print("有消息重放嫌疑")
    else:
        print("发送成功")


"""
》》》5.5.1.用户&AS服务器
    C->AS：IDc || IDtgs || TS1
    AS->C：EKc【Kc,tgs || IDtgs || TS2 || Lifetime2 || TGT】
    其中，EKc[]表示使用用户口令生成的数据包；TGT使用KDC生成的密钥加密，
    数据格式为：TGT=EKtgs【IDc || ADDRc || IDtgs || TS2|| Lifetime2 || Kc,tgs】；
    TS1、TS2为对应过程开始的时间；Lifetime2为TGT的有效期。
》》》5.5.2.用户&TGS服务器
    C->TGS：IDs || TGT || Authenticator
    TGS->C：EKc,tgs【Kc,s || IDs || TS4 || ST】
    其中，IDs为要访问的服务器的标识；Authenticator为用户生成，用于验证发出该请求的用户就是TGT中所声明的用户，
    Authenticator=EKc,tgs【IDc || ADDRc || TS3 ||Lifetime3】；
    Kc,tgs由AS生成，仅由用户和TGS共享密钥；Kc,s由TGS生成，仅由用户和服务器共享密钥；
    TS4为ST票据签发的时间；ST为访问某个服务的许可票据，ST=EKs【Kc,s || IDc || ADDRc || TS4 || Lfetime4】。
》》》5.5.3.用户&应用服务器
    C->S：ST ||  Authenticator
    S->C：EKc,s【TS5+1】
    其中，Authenticator为用户生成的，用来验证发送请求的用户就是ST中所声明的用户，Authenticator=EKc,s【IDc || ADDRc || TS5】。
"""

# 注意密码不是原密钥，是hash值 !!!
# 向as请求注册的数据结构
regist_req_as = {"id": "", "passwd": ""}
# 向as请求修改密码的数据结构
modify_pwd_as = {"id": "", "passwd_new": "", "passwd_old": ""}

# 向ss请求注册的数据结构
regist_req_ss = {"id": "", "passwd": "", "name": "", "sex": "", "address": "", "phonenumber": ""}
# 向ss请求修改密码的数据结构
modify_pwd_ss = {"id": "", "passwd_new": "", "passwd_old": ""}
# 充值余额报文信息
change_money_ss = {"id": "", "passwd": "", "money": ""}
# 查看订单详情报文
product_details_ss = {"id": "", "id_o": ""}
# 查看订单进度报文(id:客户id，id_o:订单id
order_details_ss = {"id": "", "id_o": ""}
# 修改信息报文(新旧密码)
alter_info_ss = {"id": "", "name": "", "passwd1": "", "passwd2": "", "sex": "", "address": "", "phonenumber": ""}
# 获取菜单报文
show_dish_ss = {}
#  商家
# 一键上下班
one_click_commuting = {"id": ""}
one_click_commuting2 = {"state": ""}
# 商品管理——删除商品(id:客户id，id_p:商品id)
delete_product = {"id": '', "id_p": ''}
# 商品管理——新建商品(name_p:商品名,price_p:商品价格,stock_p:商品库存)
new_product = {"id": '', "id_p": '', "name_p": '', "price_p": '', 'stock_p': ''}

#  快递员
# 修改信息 快递员，deliver
modify_info = {"id": '', "name": '', "sex": '', "phonenumber": ''}

# ACK


# ss->c报文格式,错误状态server_error,内容为error_info
# 菜单
show_dish = {"buss_name": "", "dish_name": "", "dish_money": " "}
#


# business->server报文格式：注册，登录，修改密码同客户
# 修改个人信息
# modify_info = {"id": "", "name": "", "passwd": "", "address": "", "phonenumber": ""}
modify_info = {"id": "", "name": "", "sex": "", "address": "", "phonenumber": ""}

# 一键切换上下班
one_click_commuting = {"id": ""}
# 服务段返回报文内容（切换状态后当前状态）
one_click_commuting2 = {"state": ""}

# 刷新订单：id:商家id
refresh_order = {"id": ""}
# 查看商品详情
product_details = {"id": ""}
# 修改商品信息:id：商家id，  id_d:菜品id ，name：菜品名字， price：菜品单价，stock：菜品库存
modify_product = {"id": "", "id_d": "", "name": "", "price": "", "stock": ""}
# 删除商品：
delete_product = {"id": "", "id_d": ""}
# 完成订单：
finish_order = {"id": "", "id_o": ""}
# 余额提现：
cash_out = {"id": "", "passwd": "", "money": ""}

# ss->bussiness


# ss->rider

"""
customer:

"""
"""
请求注册和修改密码，返回报文的content为空，成功则state字段为success，否则为error

"""


def tuple_2_dict(list_key: tuple, list_value: tuple) -> str:
    """
    将传入的一个列表作为标题，另一个作为值，转换成一个dict并且返回。
    :param list_key: 键
    :param list_value: 值
    :return:  返回一个由目标dict转换成的string，后续可以由dict(eval(xxx))还原
    """
    if len(list_key) != len(list_value):
        raise ValueError("key的长度" + str(len(list_key)) + "不等于value的长度" + str(len(list_value)))
    ans_dict = dict()
    for i in range(len(list_key)):
        ans_dict[list_key[i]] = list_value[i]

    return str(ans_dict)


def tuple_2_dict_v2(list_key: tuple, list_value: tuple) -> str:
    """
    将传入的一个列表作为标题，另一个作为值，转换成一个dict并且返回。
    :param list_key: 键，例如：BB = ("x", "y")
    :param list_value: 值,例如：AA = (("a", 1), ("b", 2), ("c", 3), ("d", 4))
    :return:  返回一个由目标dict转换成的string，后续可以由dict(eval(xxx))还原
    """
    if len(list_key) != len(list_value[0]):
        raise ValueError("key的长度" + str(len(list_key)) + "不等于value的长度" + str(len(list_value[0])))
    ans_dict = dict()

    num = 0
    for _tuple in list_value:
        num += 1
        ans_dict["item" + str(num)] = dict()
        for i in range(len(list_key)):
            ans_dict["item" + str(num)][list_key[i]] = _tuple[i]

    return str(ans_dict)


if __name__ == "__main__":
    compare_time()

    # a = ("oo", "pp", "qq")
    # x = {'a': 1, 'b': 2, 'c': 3}
    # y = {'a': 1, 'b': 2, 'c': 3}
    # z = {'a': 1, 'b': 2, 'c': 3}
    # XXX = (x, y, z)
    # b = (1, 2, 3)
    # st = tuple_2_dict(a, XXX)
    # print(st)
    # # bbb = {"A": 1,
    # #        "B":
    # #            {'a': 1, 'b': 2, 'c': 3}}
    # # bbb[1]["gno"] =
    # for i in dict(eval(st)).keys():
    #     print(i)
    #     print(dict(eval(st))[i])

    AA = (("a", 1), ("b", 2), ("c", 3), ("d", 4))
    BB = ("x", "y")
    st_ = tuple_2_dict_v2(BB, AA)
    print(len(st_), st_)

    # 下面是不用转dict的另一种方法：（直接把两个tuple组合起来发，第一个元素为标题，其他为内容，仿照csv文件的每一行）
    AA_ = list(AA)
    AA_.insert(0, BB)
    AA_2 = str(AA_)
    print(len(AA_2), AA_2)

    print("方法二比方法一减少", len(st_) - len(AA_2), "个bit")

    # 发送AA_2 接收方的解析方法：
    # 第一个元素为标题
    XX = list(eval(AA_2))
    for i in range(len(XX) - 1):
        print("\nitem", i + 1, ":    ", end="")
        for j in range(len(XX[0])):
            print(XX[0][j], "--", XX[i + 1][j], end="\t")
