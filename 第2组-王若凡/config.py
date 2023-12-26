# -*- coding: utf-8 -*-
# @Time : 2022/4/26 09:36
# @Author : cheney
# @File : config.py
# @Software: PyCharm
# @Site: www.cheney.cc

"""
说明：
    这里存的是一些配置信息。
    在自己的文件里面import config然后就能读取下面这些变量
    后续如果需要改动信息，就只需要改config 这一个文件即可
    主要是为了方便调试
    编程最后可以把这个文件删除，改成固定的。
"""

'''KDC部分的信息'''
port_as = 15101
addr_as = "127.0.0.1"

port_tgs = 15102
addr_tgs = "127.0.0.1"

'''外卖系统部分'''
port_ss_client = 15031
port_ss_deliver = 15032
port_ss_store = 15033
addr_ss = "127.0.0.1"
# 客户端不需要，因为客户端总是主动发起请求的一方

'''数据库部分'''
port_mysql = 3306
addr_mysql = "127.0.0.1"
mysql_user = "admin"
mysql_passwd = "admin"
mysql_db = "abc"

redis_port = 6379
redis_addr = '127.0.0.1'
#redis_auth = "auth"
redis_auth = "c5123456"
redis_db0_ = 0  # kcv
redis_db1_ = 1  # ktgs
redis_db2_ = 2  # kv

