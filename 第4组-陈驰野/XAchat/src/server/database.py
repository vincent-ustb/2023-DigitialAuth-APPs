import pymysql

class ServerDataBase:
    def __init__(self) -> None:
        # 创建数据库连接
        self.db = pymysql.connect(
            host='127.0.0.1',  # 要连接的主机地址
            user='root',  # 登录数据库的用户
            password='glgjss17yfhbqz',  # 密码
            database='xachat'  # 要连接的数据库
        )
        self.history_id = 0

    # 获取用户数据
    def get_users(self) -> dict[str, str]:
        cursor = self.db.cursor()
        cursor.execute("select * from users;")
        data = cursor.fetchall()
        cursor.close()
        return dict(data)

    # 加载历史记录
    def get_history(self) -> dict[(str, str): list[(str, str, str)]]:
        cursor = self.db.cursor()
        cursor.execute("select * from history;")
        data = cursor.fetchall()
        cursor.close()
        # 更新下一个要保存的记录id
        if data != ():
            self.history_id = data[-1][0]
        ret = {}
        for line in data:
            ret[(line[1], line[2])].append((line[1], line[3], line[4]))
        return ret

    # 添加用户数据
    def add_users(self, username, password):
        cursor = self.db.cursor()
        cursor.execute("insert into users values ('{}', '{}');".format(username, password))
        cursor.close()
        self.db.commit()
    