# -*- coding: utf-8 -*-
# @Time : 2022/4/23 16:23
# @Author : cheney
# @File : log.py
# @Software: PyCharm
# @Site: www.cheney.cc

from datetime import datetime
import traceback
import os


def debug(content: str, path: str = "./", log_name: str = "log.txt") -> bool:
    """
    :param content: 要写到日志里面的内容
    :param path: 写日志的路径 默认为当前目录
    :param log_name: 日志文件名 默认为log.txt
    :return: 是否写成功
    """
    if not os.path.isdir(path):
        a = os.getcwd()
        os.makedirs(a+'\\'+path)
        # 这里进行错误处理 !!! 待完善
        #return False


    f = open(path+log_name, 'a')  # 追加写
    f.write("\n")
    dt = str(datetime.now())  # 获取当前时间
    # caller_filename = traceback.extract_stack()[-2][0]
    f.write(dt)
    f.write("\n")
    caller_filename = ""
    for i in traceback.extract_stack():  # 获得调用log的文件名以及对应的行
        # caller_filename += str(i)
        f.write(str(i))
        f.write("\n")
    f.write(content + "\n" + "_"*50 + "\n")
    f.close()

    return True


if __name__ == '__main__':
    status = debug("这是一个测试信息，测试输出log的功能")
    if status:
        print("写日志成功")
    else:
        print("写日志失败")
    # cbkajbcabcabokc
