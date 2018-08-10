'''
    Sql进程池的方式进行连接
    Author: Ribbon Huang
    Date: 2018-07-26
'''
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
                return len(results)
            except:
                logger.warning('Error: unable to fecth datas')

    def fetchAllData(self, sql):
        '''搜索所有符合sql语句查找出来的资料'''
        with SqlConnectionPool() as db:
            try:
                db.cursor.execute(sql)
                results = db.cursor.fetchall()
                return results
            except:
                logger.warning('Error: unable to fecth datas')

    def fetchOne(self, sql):
        '''搜索一条sql语句查找出来的资料'''
        with SqlConnectionPool() as db:
            try:
                db.cursor.execute(sql)
                results = db.cursor.fetchone()
                print(results)
            except:
                logger.warning('Error: unable to fecth data')

    def addIp(self, sql ,ips):
        '''对mysql进行添加进资料库的操作'''
        with SqlConnectionPool() as db:
            try:
                for info in ips:
                    param = (info['ip'], info['port'], info['type'])
                    db.cursor.execute(sql, param)
                    db.conn.commit()
            except:
                logger.warning('Error: Unable to add datas')

    def addTest(self, sql ,ip):
        '''对mysql进行添加进资料库的操作'''
        with SqlConnectionPool() as db:
            try:
                param = (ip['ip'], ip['port'], ip['type'])
                db.cursor.execute(sql, param)
                db.conn.commit()
            except:
                logger.warning('Error: Unable to add datas')

    def updateIp(self, sql, ip):
        with SqlConnectionPool() as db:
            try:
                param = (ip['id'],)
                db.cursor.execute(sql, param)
                db.conn.commit()
            except:
                logger.warning('Error: Unable to add datas')

if __name__ == '__main__':
    sql = 'UPDATE useip SET  isuse=0 where id=%s'
    ip = {'id':307}
    db = SqlUtile().updateIp(sql=sql, ip = ip)

logger.removeHandler(fileHandler)