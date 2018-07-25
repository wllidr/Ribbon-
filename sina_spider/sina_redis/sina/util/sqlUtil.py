import re

from pymysql import DatabaseError
from sina.util.verify import code_verificate
from sina.settings import MYSQL_USER, MYSQL_PORT, MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD
import pymysql
import logging

# 记录日常日志
logger = logging.getLogger('sqlError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('sqlError.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)

class DBUtil:
    def __init__(self):
        dbConfig = {
            'host' : MYSQL_HOST,
            'port' : MYSQL_PORT,
            'database' : MYSQL_DB,
            'user' : MYSQL_USER,
            'password' : MYSQL_PASSWORD,
            'charset' : 'utf8'
        }
        self.connect = pymysql.connect(**dbConfig)
        if self.connect:
            self.cursor = self.connect.cursor()
        else:
            raise Exception('数据库连接参数有误')
            logger.warning('数据库连接参数有误')

    def fetchOne(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            return data
        except DatabaseError as e:
            logger.warning('sql语句有误：' + sql)

    def fetchAll(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            return data
        except DatabaseError as e:
            logger.warning('sql语句有误：' + sql)

    def otherOprate(self, sql, params):
        self.cursor.execute(sql, params)
        self.cursor.connection.commit()

    def close(self):
        self.cursor.close()
        self.connect.close()

if __name__ == '__main__':
    item = {'blogger': '5235640836',
             'comeFrom': '2016-03-07 23:54:51&nbsp;来自微博 weibo.com',
             'commentNumber': '评论[0]',
             'content': '告别单身，马上就加入到腾讯女性 ',
             'goodNumber': '赞[3]',
             'transmitNumber': '转发[1]'}
    db = DBUtil()
    sql = 'INSERT INTO weibo(blogger, content, comeFrom, goodNumber, transmitNumber, commentNumber) ' \
                  'VALUES (%s, %s, %s, %s ,%s, %s)'
    item['comeFrom'] = re.sub('&nbsp;','',item['comeFrom'])
    params = (item['blogger'], item['content'], item['comeFrom'], item['goodNumber'], item['transmitNumber'], item['commentNumber'])
    print(params)
    db.otherOprate(sql, params=params)
    print(2222)

logger.removeHandler(fileHandler)