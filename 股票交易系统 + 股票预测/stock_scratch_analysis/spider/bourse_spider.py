'''
    Author : Ribbon Huang
    Date : 2018 - 08 - 06
    Desc :
        上海交易所，通过爬取的凤凰网代码号，针对交易所JSON传递网址，来获取当天交易的所有情况信息
        http://yunhq.sse.com.cn:32041/v1/sh1/line/代码号?callback=jQuery111209283061309370473_时间戳&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=时间戳
'''
# import gevent.monkey;gevent.monkey.patch_all()
# import gevent
import threadpool
import json
import random
import time
import requests
from requests.exceptions import ConnectionError, MissingSchema, ConnectTimeout, InvalidURL, ChunkedEncodingError, ReadTimeout
from conf.settings import MIN_WAIT_TIME, MAX_WAIT_TIME, NUM_RETRIES, LOGGER_SPIDER_NAME, THREADS_NUM, STATUS_CODES
from utils.logger import LOGGER
from utils.userAgent import USER_AGENTS
from utils.sqlUtil import SqlUtile
from utils.mongou import MongoUse

logger = LOGGER.createLogger(LOGGER_SPIDER_NAME)
db = SqlUtile()
mongo = MongoUse()
'''
    上海交易所当天，特定股票代码的信息爬取
'''
class BourseSpider:
    def __init__(self, code):
        timestamp = int(time.time())
        self.url = 'http://yunhq.sse.com.cn:32041/v1/sh1/line/' + str(code) + '?callback=jQuery111209283061309370473_'\
                    + str(timestamp - random.randint(5, 15)) +'&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=' \
                    + str(timestamp)

    def changeUseAgent(self):
        # 改变浏览器头信息
        user_agent = random.choice(USER_AGENTS)
        self.headers = {
            'User-Agent': user_agent
        }

    def changeProxy(self):
        # 用于更改代理IP
        pass

    def crawlPage(self, url, num_retries = NUM_RETRIES):
        # 爬虫爬取页面
        html = ''
        try:
            self.response = requests.get(url, headers=self.headers)
            if self.response.status_code == STATUS_CODES['ok']:
                html = self.response
            elif STATUS_CODES['clientError'] <= self.response.status_code < STATUS_CODES['severError']:
                # 客户端错误则直接返回
                logger.warning('Bourse_Spider: Client have error')
            elif STATUS_CODES['severError'] <= self.response.status_code < STATUS_CODES['limit']:
                if self.num_retries > 0:
                    # 服务端崩溃类错误，进行休眠，等待一段时间重新测试服务器是否恢复，总共5次机会一个网页
                    time.sleep(random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME))
                    html = self.crawlPage(url, num_retries = num_retries - 1)
        except ConnectionError:
            logger.warning('Bourse_Spider: requests.exceptions.ConnectionError')
        except MissingSchema or InvalidURL:
            logger.warning('Bourse_Spider: requests.exceptions.MissingSchema Or requests.exceptions.InvalidURL')
        except ChunkedEncodingError:
            logger.warning('Bourse_Spider: requests.exceptions.ChunkedEncodingError')
        except ConnectTimeout or ReadTimeout:
            logger.warning('Bourse_Spider: requests.exceptions.ConnectTimeout Or requests.exceptions.ReadTimeout')
        except Exception as e:
            logger.warning(e)
        if html != '':
            self.crawlInfos(html)

    def crawlInfos(self, html):
        #  提取页面的信息， 并且直接存储如mongoDB
        htmlTemp = html.text
        htmlTemp = htmlTemp.split('(')[1]
        htmlTemp = htmlTemp.split(')')[0]
        info = json.loads(htmlTemp)
        mongo.insertDb(info)
        # print(info)

'''
    爬虫爬取的所有逻辑
'''
def bourse_begin(code):
    bourse = BourseSpider(code=code)
    bourse.changeUseAgent()
    bourse.crawlPage(bourse.url)

'''
    线程池，协程调用
'''
def bourse_spider_start():
    sql = 'SELECT code FROM finance'
    codes = db.findAll(sql)

    # 协程
    # spawns = []
    # for code in codes:
    #     spawns.append(gevent.spawn(bourse_begin, code))
    # gevent.joinall(spawns)

    # 线程池
    pool = threadpool.ThreadPool(THREADS_NUM)
    requests = threadpool.makeRequests(bourse_begin, codes)
    [pool.putRequest(req) for req in requests]
    pool.wait()

if __name__ == '__main__':
    bourse_spider_start()

LOGGER.removeLogger()