'''
    Sql进程池的方式进行连接
    Author: Ribbon Huang
    Date: 2018 -11 - 19
'''

__author__ = 'Ribbon Huang'
from DBUtils.PooledDB import PooledDB
import conf.settings as Config
import pymysql
from pymysql import DatabaseError
import logging

'''
    记录日常日志
'''
logger = logging.getLogger('sqlError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('sqlError.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)

'''
    Mysql数据库连接池
'''
class SqlConnectionPool(object):
    __pool = None

    def __enter__(self):
        '''单个用户连接进入连接池后，即可以执行sql语句进行查询'''
        try:
            self.conn = self.__getConn()
            self.cursor = self.conn.cursor()
        except DatabaseError:
            logger.warning('sql connect error')
        except Exception as e:
            logger.warning('sql undefined error' + e)
        return self

    def __getConn(self):
        '''连接池的方式连接mysql资料库'''
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=Config.DB_MIN_CACHED , maxcached=Config.DB_MAX_CACHED,
                                   maxshared=Config.DB_MAX_SHARED, maxconnections=Config.DB_MAX_CONNECYIONS,
                                   blocking=Config.DB_BLOCKING, maxusage=Config.DB_MAX_USAGE,
                                   setsession=Config.DB_SET_SESSION,
                                   host=Config.DB_TEST_HOST , port=Config.DB_TEST_PORT ,
                                   user=Config.DB_TEST_USER , passwd=Config.DB_TEST_PASSWORD ,
                                   db=Config.DB_TEST_DBNAME , use_unicode=False, charset=Config.DB_CHARSET)

        return self.__pool.connection()

    def __exit__(self, type, value, trace):
        '''连接池的释放'''
        self.cursor.close()
        self.conn.close()

'''
    mysql操作的调用
'''
class SqlUtile:
    def fetchAll(self, sql):
        '''搜索所有符合sql语句查找出来的资料'''
        with SqlConnectionPool() as db:
            try:
                db.cursor.execute(sql)
                results = db.cursor.fetchall()
                return results
            except:
                logger.warning('Error: unable to fecth datas')

    def insert(self, sql, params):
        '''搜索所有符合sql语句查找出来的资料'''
        with SqlConnectionPool() as db:
            try:
                db.cursor.execute(sql, params)
                db.conn.commit()
            except:
                logger.warning('Error: unable to insert datas')

if __name__ == '__main__':
    sql = 'insert into new1 VALUES ("2","3","4")'
    dd = SqlUtile().insert(sql)


logger.removeHandler(fileHandler)