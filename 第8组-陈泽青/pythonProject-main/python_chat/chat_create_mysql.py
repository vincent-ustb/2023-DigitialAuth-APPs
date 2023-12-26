import pymysql
Connection = pymysql.connect(host="localhost", user="root", password="czq2003718", db="python_chat", port=33061)
cursor = Connection.cursor()
sql_create_table = '''

    create table user_information
     (
      user_name varchar (255),
      
      password varchar (255),
      
      data BLOB


    )

'''
cursor.execute(sql_create_table)
cursor.close()
