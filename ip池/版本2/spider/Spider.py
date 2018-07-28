'''
    多进程 + 线程池
    Author : Ribbon Huang
    DATE  : 2018-07-26
'''
import logging
import re
import sys
import time
from requests.exceptions import ConnectionError, MissingSchema, ConnectTimeout, InvalidURL, ChunkedEncodingError, ReadTimeout
from conf.settings import PARSE_LIST, MIN_WAIT_TIME, MAX_WAIT_TIME, MIN_IP_NUMBERS, MAX_IP_NUMBERS
import requests
from util.userAgent import USER_AGENT
import random
from util.sqlUtil import SqlUtile
from multiprocessing import Pool, Manager
from util import redisuse


# 记录日常日志
logger = logging.getLogger('spiderError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('spiderError.log')
fileHandler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)
logger.addHandler(console_handler)

# 随机选择一个网页
parse_list = random.choice(PARSE_LIST)
db = SqlUtile() #DB使用
# 获取页面
def get_html(url, num_retries = 5):
    agent = random.choice(USER_AGENT)
    headers = {'User-Agent' : agent}
    html = ''
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response
        elif 400 <= response.status_code < 500:
        # 客户端错误则直接返回
            logger.warning('Client have error')
        elif 500 <= response.status_code < 600:
            if num_retries > 0:
        # 服务端崩溃类错误，进行休眠，等待一段时间重新测试服务器是否恢复，总共5次机会一个网页
                time.sleep(random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME))
                html = get_html(url, num_retries = num_retries - 1)
    except ConnectionError:
        logger.warning('requests.exceptions.ConnectionError')
    except MissingSchema or InvalidURL:
        logger.warning('requests.exceptions.MissingSchema Or requests.exceptions.InvalidURL')
    except ChunkedEncodingError:
        logger.warning('requests.exceptions.ChunkedEncodingError')
    except ConnectTimeout or ReadTimeout:
        logger.warning('requests.exceptions.ConnectTimeout Or requests.exceptions.ReadTimeout')
    except Exception as e:
        logger.warning(e)
    return html

# 页面进行解析
def get_datas(html):
    ips = []
    try:
        pattern = parse_list['regular']
        datas = re.findall(pattern, html)
        for data in datas:
            try:
                type = data[2]
            except:
                type = 'HTTP'
            ips.append({'ip' : data[0].strip(), 'port' : data[1].strip(), 'type' : type})
    except Exception as e:
        logger.warning(e)
    # 使用redis去重IP， 省去重复验证的过程
    ips = redisuse.redis_bloomfilter(ips)
    return ips

# 解析的资料进入资料库
def load_database(ips):
    print(ips)
    sql = 'INSERT INTO ips (ip, port, type) VALUES (%s, %s, %s)'
    db.addIp(sql, ips)

# 爬虫从请求页面、获取页面、解析页面、资料入库的流程，全部集成在spider_process函数中
def spider_process(url, q):
    html = get_html(url)
    print(html)
    if html != '':
        ips = get_datas(html.text)
        if len(ips):
            # load_database(ips)
            # validator.start_valida(ips)
            # sql = 'SELECT * FROM useip where isuse=1'
            # num = db.fetchAll(sql)
            q.put(1)
            print(ips)

def spider_start():
    # print(PARSE_LISTS[3])
    urls = parse_list['urls']
    print(urls)
    sql = 'SELECT * FROM useip where isuse=1'
    num = db.fetchAll(sql)
    # 获取可用IP的数量，如果没有低于最低IP的数量则不进入进程池中进行爬取工作
    if num < MIN_IP_NUMBERS:
        print(1111)
        # 创建进程池, 池中数量小于最小IP池的时候
        p = Pool()
        q = Manager().Queue()  # 进程池通信需要的队列
        # 多进行方式进行爬取IP
        print(2222)
        for url in urls:
            print(url)
            p.apply_async(func=spider_process, args=(url, q))
        # p.close()
        while num <= MAX_IP_NUMBERS:
            # 等待进程池的操作
            ipNum = q.get()
            num = ipNum
            print('当前的ip池的数量:', num)
        else:
            p.terminate()
        p.join()

if __name__ == '__main__':
    spider_start()

logger.removeHandler(fileHandler)
logger.removeHandler(console_handler)
