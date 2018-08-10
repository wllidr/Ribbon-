"""
MongoDB连接池模块
"""
from pymongo import MongoClient


class MongoPool(object):
    """
    MongoDB连接池
    复习了默认参数数的用法和自定义异常
    子类调用父类构造函数super(子,self).__init__(*args)
    isinstance(max_conn, int)的用法
    """

    def __init__(self, uri, max_conn=30):
        """
        :param max_conn: 最大连接数 默认30 必须是1到200之间的整数
        :param uri: 数据库连接uri mongodb://username:password@localhost:27017
        """

        # 如果max_conn为空或者不是1到200之间的整数 抛出异常
        if not max_conn or not isinstance(max_conn, int) or max_conn > 200 or max_conn < 1:
            raise MongoPoolInitException(errorMsg='客官，max_conn不可以等于{}哦'.format(max_conn))
        self.__max_conn = max_conn
        self.__conn_list = []
        self.__uri = uri
        self.__idle = self.__max_conn
        self.__busy = 0
        self.__prepare_conn()

    def __prepare_conn(self):
        """
        根据参数max_conn初始化连接池
        :return: None
        """
        try:
            for x in range(0, self.__max_conn):
                conn_dict = {'conn': MongoClient(self.__uri), 'busy': False}
                self.__conn_list.append(conn_dict)
            print(len(self.__conn_list))
            print(self.__idle)
        except Exception as e:
            raise MongoPoolException('Bad uri: {}'.format(self.__uri))

    def get_conn(self):
        """
        从连接池中获取一个MongoDB连接对象
        :return: mongodb_connection
        """
        if self.__idle < 1:
            raise MongoPoolOutOfConnections(errorMsg='不好啦！Mongo的连接数不够用了！')
        for index in range(0, len(self.__conn_list)):
            conn = self.__conn_list[index]
            if conn.get('busy') == False:
                conn['busy'] = True
                self.__busy += 1
                self.__idle -= 1
                return conn.get('conn')

    def close(self, conn):
        """
        将参数中的连接池对象的busy改为False，标识此连接为空闲状态
        :param conn: mongoDB数据库连接对象
        :return: None
        """
        for index in range(0, len(self.__conn_list)):
            inner_conn = self.__conn_list[index]
            if inner_conn.get('conn') == conn:
                inner_conn['busy'] = True
                self.__busy -= 1
                self.__idle += 1
                inner_conn['busy'] = False
                break
            else:
                raise MongoPoolException("你特么的在逗我呢！这个连接不是从我这借的，我不要！")


class MongoPoolInitException(Exception):
    """
    初始化异常
    """

    def __init__(self, errorMsg):
        super(MongoPoolInitException, self).__init__(errorMsg)


class MongoPoolOutOfConnections(Exception):
    """
    连接数不够用了
    """

    def __init__(self, errorMsg):
        super(MongoPoolOutOfConnections, self).__init__(errorMsg)


class MongoPoolException(Exception):
    """
    MongoPool其他异常
    """

    def __init__(self, errorMsg):
        super(MongoPoolException, self).__init__(errorMsg)

if __name__ == '__main__':
    db = MongoPool('localhost:8000')
    db.get_conn()