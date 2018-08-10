'''MYSQL类化使用'''
import pymysql
from conf.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWD

class MysqlUse:
    def __init__(self, host = MYSQL_HOST, port = MYSQL_PORT, user = MYSQL_USER,
                 passwd = MYSQL_PASSWD, db = MYSQL_DB, charset = 'utf8'):
        self.db = pymysql.Connect(host = host, port = port, user = user,
                                  passwd = passwd, db = db, charset = charset)
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def excute(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        self.close()

    def fetch(self, sql):
        self.cursor.execute(sql)
        datas = self.cursor.fetchall()
        # print(datas)
        # for data in datas:
        #     print(data)
        self.close()
        return datas

if __name__ == '__main__':
    mysql = MysqlUse()
    datas = mysql.fetch()
    print(datas)
