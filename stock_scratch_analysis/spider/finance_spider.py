'''
    Author : Ribbon Huang
    Date : 2018 - 08 - 06
    Desc :
        凤凰财经获取一天的基本信息，这里的股市每个股票当天的基本信息。这里的爬取信息存储到资料库中。
        http://app.finance.ifeng.com/list/stock.php?t=ha&f=chg_pct&o=desc&p= + 页面
'''
import random
import re
import time
from conf.settings import MIN_WAIT_TIME, MAX_WAIT_TIME, NUM_RETRIES, LOGGER_SPIDER_NAME, MIN_PAGE, MAX_PAGE, STATUS_CODES
import requests
from utils.logger import LOGGER
from utils.userAgent import USER_AGENTS
from requests.exceptions import ConnectionError, MissingSchema, ConnectTimeout, InvalidURL, ChunkedEncodingError, ReadTimeout
from multiprocessing import Pool
from utils.sqlUtil import SqlUtile

logger = LOGGER.createLogger(LOGGER_SPIDER_NAME)
db = SqlUtile()

'''
    凤凰财经网信息爬取的爬虫逻辑
'''
class PhoenixSpider:
    def __init__(self):
        self.urls = ['http://app.finance.ifeng.com/list/stock.php?t=ha&f=chg_pct&o=desc&p=' + str(i) for i in range(MIN_PAGE, MAX_PAGE)]

    def changeUseAgent(self):
        # 该函数用于改变浏览器头信息
        user_agent = random.choice(USER_AGENTS)
        self.headers = {
            'User-Agent': user_agent
        }

    def changeProxy(self):
        # 用于代理IP池的调用
        pass

    def crawlPage(self, url, num_retries = NUM_RETRIES):
        # 用于爬取页面
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
            logger.warning('Finance_spider: requests.exceptions.ConnectionError')
        except MissingSchema or InvalidURL:
            logger.warning('Finance_spider: requests.exceptions.MissingSchema Or requests.exceptions.InvalidURL')
        except ChunkedEncodingError:
            logger.warning('Finance_spider: requests.exceptions.ChunkedEncodingError')
        except ConnectTimeout or ReadTimeout:
            logger.warning('Finance_spider: requests.exceptions.ConnectTimeout Or requests.exceptions.ReadTimeout')
        except Exception as e:
            logger.warning(e)
        if html != '':
            self.crawlInfos(html)

    def crawlInfos(self, html):
        # 用于提取页面元素
        pattern = r'<tr>[\s\S]*?<td><a [\s\S]*?>([\s\S]*?)</a></td>[\s\S]*?<td><a [\s\S]*?>([\s\S]*?)</a></td>' \
                  r'[\s\S]*?<td><span[\s\S]*?>([\s\S]*?)</span></td>[\s\S]*?<td><span[\s\S]*?>([\s\S]*?)</span>' \
                  r'</td>[\s\S]*?<td><span[\s\S]*?>([\s\S]*?)</span></td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?<td>' \
                  r'([\s\S]*?)</td>[\s\S]*?<td><span[\s\S]*?>([\s\S]*?)</span></td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?' \
                  r'<td><span[\s\S]*?>([\s\S]*?)</span></td>[\s\S]*?<td><span[\s\S]*?>([\s\S]*?)</span></td>'
        text = html.text
        infos = []
        temps = re.findall(pattern, text)
        for temp in temps:
            info = {}
            info['code'] = temp[0]
            info['name'] = temp[1]
            info['newprice'] = temp[2]
            info['pricelimit'] = temp[3]
            info['changeamount'] = temp[4]
            info['turnover'] = temp[5]
            info['volume'] = temp[6]
            info['daystartprice'] = temp[7]
            info['yesterdayprice'] = temp[8]
            info['lowest'] = temp[9]
            info['hightest'] = temp[10]
            if float(temp[2]) < float(temp[8]):
                info['pricelimit'] = '-' + info['pricelimit']
                info['changeamount'] = '-' + info['changeamount']
            infos.append(info)
        self.saveDatabase(infos)

    def saveDatabase(self, infos):
        # 用于存储数据库
        sql = 'INSERT INTO finance (code, name, newprice, pricelimit, changeamount, turnover, ' \
              'volume, daystartprice, yesterdayprice, lowest, hightest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        db.addInfos(sql, infos)

'''
    爬虫所有的逻辑的调用
'''
def finance_spider_start():
    phoenix = PhoenixSpider()
    phoenix.changeUseAgent()
    crawl = phoenix.crawlPage
    pool = Pool()
    for url in phoenix.urls:
        pool.apply_async(func=crawl, args=(url,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    finance_spider_start

LOGGER.removeLogger()

