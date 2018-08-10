'''
    Redis BloomFilter 去重处理
    Author: Ribbon Huang
    Date: 2018-07-26
'''
import redis
import logging

'''
    记录日常日志
'''
logger = logging.getLogger('redisError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('redisError.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)

'''
    直接建立一个连接池，然后作为参数Redis，实现多个Redis实例共享一个连接池
'''
pool = redis.ConnectionPool(host='localhost', port=6379, db = 0)
conn = redis.Redis(connection_pool=pool)

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
        self.bit_size = 1 << 25
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
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
    for id in ips:
        if bf.isContains(id['ip'], 'ip'):
            print('exists')
            err_time += 1
        else:
            print('insert')
            bf.insert(id['ip'], 'ip')
            temps.append(id)
    return temps

logger.removeHandler(fileHandler)