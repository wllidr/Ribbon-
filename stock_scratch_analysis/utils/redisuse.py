'''
    Redis BloomFilter 去重处理
    Author: Ribbon Huang
'''
import redis
from redis.exceptions import BusyLoadingError, DataError, ConnectionError
from utils.logger import LOGGER
from conf.settings import LOGGER_REDIS_NAME, REDIS_HOST, REDIS_PORT, REDIS_DB0, REDIS_KEY
# redis位大小设置， 以及redis质数的设置
from conf.settings import REDIS_PRIMSES, REDIS_BIT_SIZES

# 记录日常日志
logger = LOGGER.createLogger(LOGGER_REDIS_NAME)

'''
    直接建立一个连接池，然后作为参数Redis，实现多个Redis实例共享一个连接池
'''
try:
    pool = redis.ConnectionPool(host = REDIS_HOST, port = REDIS_PORT, db = REDIS_DB0)
    conn = redis.Redis(connection_pool=pool)
except ConnectionError:
    logger.warning('Error : Connect fail')
except BusyLoadingError:
    logger.warning('Error : BusyLoadingError')
except:
    logger.warning('Error : undefined error')

class SimpleHash:
    def __init__(self,cap,seed):
        self.cap = cap
        self.seed = seed

    def hash(self,value):
        ret = 0
        for i in range(value.__len__()):
            ret += self.seed*ret+ord(value[i])
            # print("ret的值：",ret)
        return ((self.cap-1) & ret)

'''
    BoomFilter去重
'''
class BloomFilter:
    def __init__(self):
        self.r = conn
        self.bit_size = REDIS_BIT_SIZES
        self.seeds = REDIS_PRIMSES
        self.hashFunc = []
        for i in range(self.seeds.__len__()):
            self.hashFunc.append(SimpleHash(self.bit_size,self.seeds[i]))

    '''判断是否存在， 存在返回True, 不存在返回false'''
    def isContains(self, str_input, name):
        if str_input == None:
            return False
        if str_input.__len__() == 0:
            return False
        ret = True
        for f in self.hashFunc:
            loc = f.hash(str_input)
            ret = ret & self.r.getbit(name,loc)
        return ret

    '''不存在进行添加'''
    def insert(self, str_input, name):
        for f in self.hashFunc:
            loc = f.hash(str_input)
            self.r.setbit(name, loc, 1)

def redis_bloomfilter(ips):
    temps = []
    bf = BloomFilter()
    err_time = 0
    flag = False
    for id in ips:
        try:
            flag = bf.isContains(id[REDIS_KEY], REDIS_KEY)
        except DataError:
            logger.warning('Error : DataError')
        except:
            logger.warning('Error : undefined error')
        if flag:
            print('exists')
            err_time += 1
        else:
            print('insert')
            try:
                bf.insert(id[REDIS_KEY], REDIS_KEY)
                temps.append(id)
            except DataError:
                logger.warning('Error : DataError')
            except:
                logger.warning('Error : undefined error')
    return temps

LOGGER.removeLogger()