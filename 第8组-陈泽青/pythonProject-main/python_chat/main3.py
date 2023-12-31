from tkinter import messagebox
import chat_register_panel
import chat_main_panel
import chat_login_panel
import chat_client
import threading
import time
import tkinter.filedialog   # 导入文件选择对话框模块


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

private_key = None  # 存储私钥的全局变量
public_key = None  # 存储公钥的全局变量

chat_user = "【群聊】"
import pymysql

def check_database_connection():
    try:
        # 在此处进行数据库连接的操作，例如使用 pymysql 连接 MySQL 数据库
        connection = pymysql.connect(host="localhost", user="root", password="czq2003718", db="python_chat",port=33061)
        print("数据库连接成功")
        connection.close()
    except pymysql.Error as e:
        print("数据库连接失败:", e)

# 生成密钥对的函数
def generate_key_pair():
    global private_key, public_key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # 将私钥保存到文件中（供以后使用）
    with open("E:\\third\Digital authentication\\test\\pythonProject-main\\2\\pythonProject-main\\python_chat\\rsa\\private_key.pem", "wb") as key_file:
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_file.write(pem)

    # 将公钥保存到文件中（供其他方使用）
    with open("E:\\third\Digital authentication\\test\\pythonProject-main\\2\\pythonProject-main\\python_chat\\rsa\\public_key.pem", "wb") as key_file:
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        key_file.write(pem)
    # 返回公钥
    return public_key

# 从文件加载私钥和公钥
def load_keys():
    global private_key, public_key

    # 从文件中加载私钥
    with open("E:\\third\Digital authentication\\test\\pythonProject-main\\2\\pythonProject-main\\python_chat\\rsa\\private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # 从文件中加载公钥
    with open("E:\\third\Digital authentication\\test\\pythonProject-main\\2\\pythonProject-main\\python_chat\\rsa\\public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

# 使用SHA-256进行哈希运算的函数
def hash_data(data):
    if isinstance(data, str):  # 如果是字符串类型，则进行编码
        data = data.encode('utf-8')
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    hashed_data = digest.finalize()
    return hashed_data

# 使用私钥对数据进行加密的函数
def sign_data(data):
    try:
        if isinstance(data, str):  # 如果是字符串类型，则进行编码
            data = data.encode('utf-8')
        elif not isinstance(data, bytes):  # 如果不是字符串或字节类型，则抛出异常
            raise TypeError("Data must be either a string or bytes.")

        signature = private_key.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            algorithm=hashes.SHA256()
        )
        return signature
    except Exception:
        return None


   # 验证数字签名的函数
def verify_signature(data, signature, public_key):
    try:
        if isinstance(data, str):  # 如果是字符串类型，则进行编码
            data = data.encode('utf-8')
        elif not isinstance(data, bytes):  # 如果不是字符串或字节类型，则抛出异常
            raise TypeError("Data must be either a string or bytes.")
        
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
  
def close_socket():
    print("尝试断开socket连接")
    client.client_socket.close()


def close_login_window():
    close_socket()
    login_frame.login_frame.destroy()
    #login_frame.login_frame.destroy()

def close_main_window():
    #time.sleep(5)
    client.send_message("exit", chat_user)
    #time.sleep(1)
    close_socket()
    main_frame.main_frame.destroy()

def file_open_face():
    # 打开文件对话框
    file_name = tkinter.filedialog.askopenfilename()
    # 路径不为空则读取图片并在头像中显示
    if file_name != '':
        register_frame.add_face(file_name)
    else:
        messagebox.showwarning(title="提示", message="你还没有选择文件！")


def private_talk(self):
    global chat_user
    # 获取点击的索引然后得到内容(用户名)
    indexs = main_frame.friend_list.curselection()
    index = indexs[0]
    if index > 0:
        chat_user = main_frame.friend_list.get(index)
        print("chat_user",chat_user)
        # 修改客户端名称
        if chat_user == '【群聊】':
            title = "    在线用户         python聊天室欢迎您：" + main_frame.user_name + "                       " + \
            "                           "
            main_frame.change_title(title)
        elif chat_user == main_frame.user_name:
            messagebox.showwarning(title="提示", message="自己不能和自己进行对话!")
            chat_user = '【群聊】'
        else:
            title = "                                " + main_frame.user_name + "  私聊 -> " + chat_user + \
                    "                                                    "
            main_frame.change_title(title)

# 登录按钮处理事件
def handding_login(self):
    # 调用chat_login_pannel模块的对象实例方法获取输入的用户名和密码
    user_name, password = login_frame.get_input()
    password = hash_data(password)
    # 判断用户名和密码不能为空
    if user_name == "":
        messagebox.showwarning(title="提示", message="用户名不能为空")
        return
    if password == "":
        messagebox.showwarning(title="提示", message="密码不能为空")
        return
    # 调用在此类创建的chat_client模块的对象的实例方法，如何返回True，则登录成功
    if client.login_type(user_name, password) == "1":
        go_to_main_panel(user_name)  # 调用此类的前往聊天主界面函数，参数为用户名
    else:
        messagebox.showwarning(title="提示", message="用户名或密码错误！")

# 注册按钮处理事件函数
def handding_register():
    login_frame.close_login_panel()  # 调用在此类创建的login_frame对象的实例方法关闭登录界面
    global register_frame  # 声明全局变量，方便在其他函数使用
    # 创建chat_register_panel模块的注册界面的对象，把此类关闭注册页面前往登录界面的函数close_register_window,
    # 注册按钮事件函数作为参数
    # 可以把chat_login_pannel模块的事件绑定在这几个函数上
    register_frame = chat_register_panel.RegisterPanel(file_open_face, close_register_window, 
                                                       lambda: register_submit(register_frame))
    # 调用对象的实例方法显示注册界面
    register_frame.show_register_panel()
    register_frame.load()

#
def close_register_window():
    register_frame.close_register_panel()  # 调用在此类创建的register_frame对象的实例方法关闭注册界面
    global login_frame  # 使用全局变量,可以在其他函数使用
    # 创建chat_login_panel模块的登录界面的对象，把此类登录处理函数handding_login,
    # 注册处理函数作handding_register，关闭登录界面客户端的socket的close_login_window作为参数
    # 可以把chat_login_pannel模块的事件绑定在这几个函数上
    login_frame = chat_login_panel.LoginPanel(handding_login, handding_register, close_login_window)
    login_frame.show_login_panel()  # 对象调用聊天主界面对象的实例方法显示界面
    login_frame.load()  # 调用对象实例方法加载动图

#

def register_submit(self):
    check_database_connection()
    # 调用在此类创建的对象实例方法获取用户名，密码，确认密码，头像文件路径
    user_name, password, confirm_password, file_name = register_frame.get_input()
    generate_key_pair()
    load_keys()
    hashed_password = hash_data(password)    

    # 对象调用实例方法发送消息给服务器
    signature = sign_data(hashed_password)  # 无需再次编码
    if not verify_signature(hashed_password, signature, public_key):
        messagebox.showerror("错误", "签名验证失败")
        return


    # 判断用户名，密码，确认密码是否为空
    if user_name == "" or password == "" or confirm_password == "":
        messagebox.showwarning("不能为空", "请完成注册表单")
        return

    # 判断密码和确认密码是否一致
    if not password == confirm_password:
        messagebox.showwarning("错误", "两次密码输入不一致")
        return

    # 调用在此类创建的client对象的实例方法发送信息给服务器
    # 如果返回0则注册成功
    if register_frame.file_name == "":
        messagebox.showwarning("错误", "请选择头像！")
        return
 
    # 对象调用实例方法发送消息给服务器
    result = client.register_user(user_name,  hashed_password, file_name)
    if result == "0":
        # 注册成功，跳往登陆界面
        messagebox.showinfo("成功", "注册成功")
        close_register_window()  # 调用函数关闭注册页面前往登录界面函数
    # 返回1则用户名重复
    elif result == "1":
        # 用户名重复
        messagebox.showerror("错误", "该用户名已被注册")
    # 其他错误
    elif result == "2":
        # 未知错误
        messagebox.showerror("错误", "发生未知错误")

# 发送消息按钮处理事件
def send_message(self):
    global chat_user
    print("send message:")
    # 调用调用在此类创建的chat_main_panel模块的对象的实例方法获取发送内容
    content = main_frame.get_send_text()
    # 判断内容是不是为空
    if content == "" or content == "\n":
        messagebox.showwarning(title="提示", message="空消息，拒绝发送")
        return
    print(content)
    # 调用调用在此类创建的chat_main_panel模块的对象的实例方法情况输入框的内容
    main_frame.clear_send_text()
    # 调用在此类创建的chat_client模块的对象的实例方法发送聊天内容给服务器
    client.send_message(content, chat_user)


def send_mark(exp):
    global chat_user
    # 调用在此类创建的chat_client模块的对象的实例方法发送相应内容给服务器
    client.send_message(exp, chat_user)

# 刷新用户列表按钮处理事件
def refurbish_user():
    client.send_mark()

# 关闭登陆界面前往主界面
def go_to_main_panel(user_name):
    login_frame.close_login_panel()  # 调用login_frame对象的实例方法关闭窗口
    global main_frame  # # 声明全局变量，可以在类中的其他函数使用
    # 创建chat_main_panel模块的对象，把用户名，此类的发送消息函数，发送表情包标记，
    # 打开文件按钮作为参数
    # 可以把chat_main_panel模块的事件绑定在这几个函数上
    main_frame = chat_main_panel.MainPanel(user_name, send_message, send_mark,refurbish_user, private_talk, close_main_window)
    # 创建子线程专门负责接收并处理数据
    threading.Thread(target=recv_data).start()
    main_frame.show_main_panel()  # 对象调用聊天主界面对象的实例方法显示界面
    main_frame.load()  # 调用对象实例方法加载动图

# 处理消息接收的线程方法
def recv_data():
    # 暂停1秒，等主界面渲染完毕
    time.sleep(1)
    while True:
        try:
            # 首先获取处理数据类型，然后做相应处理
            data_type = client.recv_all_string()  # 调用对象实例方法获取服务器发的消息
            print("recv type: " + data_type)
            # 获取当前在线用户列表
            if data_type == "#!onlinelist#!":
                print("获取在线列表数据")
                online_list = list()  # 创建列表存储用户
                online_number = client.recv_number()
                for n in range(online_number):  # 对象调用实例方法获取服务器发的在线用户人数
                    # 对象每次调用实例方法获取服务器发的用户名，然后添加到列表中
                    online_list.append(client.recv_all_string())
                # 对象调用实例方法刷新聊天界面用户在线列表
                main_frame.refresh_friends(online_number, online_list)
                print(online_list)
            elif data_type == "#!message#!":
                print("获取新消息")
                # 调用对象实例方法获取服务器发送的用户名
                chat_flag = client.recv_all_string()
                user = client.recv_all_string()
                print("user: " + user)
                # 调用对象实例方法获取服务器发送的内容
                content = client.recv_all_string()
                print("message: " + content)
                # 对象调用实例方法把用户名和消息显示在聊天界面
                main_frame.show_send_message(user, content, chat_flag)
        except Exception as e:
            print("接受服务器消息出错，消息接受子线程结束。" + str(e))
            break

#  前往登录界面，同时开启客户端口连接连接服务器的函数
def go_to_login_panel():
    global client  # 声明全局变量，可以在其他函数使用
    client = chat_client.ChatSocket()  # 创建chat_client模块中的客户端连接服务器的socket对象
    global login_frame # 声明全局变量，可以在其他函数使用
    # 创建chat_login_panel模块的登录界面的对象，把此类登录处理函数handding_login,
    # 注册处理函数作handding_register，关闭登录界面客户端的socket中close_login_window函数作为参数
    # 可以把chat_login_pannel模块的事件绑定在这几个函数上
    login_frame = chat_login_panel.LoginPanel(handding_login, handding_register, close_login_window)
    login_frame.show_login_panel()  # 对象调用聊天主界面对象的实例方法显示界面
    login_frame.load()  # 调用对象实例方法加载动图


# 入口
if __name__ == "__main__":
    go_to_login_panel()   # 调用此类的前往登录界面函数
