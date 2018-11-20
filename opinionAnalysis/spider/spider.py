'''
    Author : Ribbon Huang
    Date : 2018 - 11 - 18
    Desc :
        百度新闻爬虫编写， 只单单爬取最新的新闻。
'''
__author__ = 'Ribbon Huang'

import random
import time
import requests
from requests.exceptions import ConnectionError, MissingSchema, ConnectTimeout, InvalidURL, ChunkedEncodingError, ReadTimeout
import logging
from utils.userAgent import USER_AGENT
from conf.settings import *
import re
from lxml import etree
from utils.sqlUtil import SqlUtile
from utils.partticiple import part

# 记录日常日志
logger = logging.getLogger('spiderError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('spiderError.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)

class opinionAnalysis:
    def __init__(self):
        self.refer = ''

    def changeUseAgent(self):
        # 改变浏览器头信息
        self.headers = {
            'User-Agent': random.choice(USER_AGENT),
        }

    def changeProxy(self):
        # 用于更改代理IP
        pass

    def crawlPage(self, url, num_retries=NUM_RETRIES):
        # 爬虫爬取页面
        self.changeUseAgent()
        self.changeProxy()
        html = ''
        try:
            # 获取
            self.response = requests.get(url, headers=self.headers)
            if self.response.status_code == STATUS_CODES['ok']:
                html = self.response
            elif STATUS_CODES['clientError'] <= self.response.status_code < STATUS_CODES['severError']:
                # 客户端错误则直接返回
                logger.warning('Spider: Client have error')
            elif STATUS_CODES['severError'] <= self.response.status_code < STATUS_CODES['limit']:
                if self.num_retries > 0:
                    # 服务端崩溃类错误，进行休眠，等待一段时间重新测试服务器是否恢复，总共5次机会一个网页
                    time.sleep(random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME))
                    html = self.crawlPage(url, num_retries=num_retries - 1)
        except ConnectionError:
            logger.warning('Spider: requests.exceptions.ConnectionError')
        except MissingSchema or InvalidURL:
            logger.warning('Spider: requests.exceptions.MissingSchema Or requests.exceptions.InvalidURL')
        except ChunkedEncodingError:
            logger.warning('Spider: requests.exceptions.ChunkedEncodingError')
        except ConnectTimeout or ReadTimeout:
            logger.warning('Spider: requests.exceptions.ConnectTimeout Or requests.exceptions.ReadTimeout')
        except Exception as e:
            logger.warning(e)
        return html

    def crawlNewsWebsite(self, html):
        # 获取各类新闻头条的新闻以及网站
        html = html.content.decode('utf8','ignore')
        news = re.findall('<a href="(http[\s\S]*?)"[\s\S]*?target[\s\S]*?>([\s\S]*?)</a>', html)
        for new in news:
            if new[1].strip() == '' or new[1] == '个性推荐' or new[1] == 'iPhone版下载' or new[1] == 'Android版下载' or re.search('src', new[1]):
                pass
            else:
                newsHtml = self.crawlPage(new[0])
                self.crawlNews(new[1], newsHtml, new[0])

    def crawlNews(self, newsTitle, newsHtml, newWebsite):
        # 获取新闻的详情
        try:
            new = re.findall('<!--mainContent begin-->([\s\S]*?)<!--mainContent end-->', newsHtml.content.decode('utf8','ignore'))
        except:
            new = re.findall('<!--mainContent begin-->([\s\S]*?)<!--mainContent end-->', newsHtml.text)
        info = ''
        if new:
            pass
        else:
            try:
                html = etree.HTML(newsHtml.content.decode('utf8'))
            except:
                html = etree.HTML(newsHtml.content.decode('gb2312', 'ignore'))
            new = html.xpath('//div[@class="news_txt"]/text()')
            if not new:
                new = html.xpath('//p/text()')

        try:
            for i in new:
                i = re.sub('<.*?>', '', i)
                i = re.sub('原标题', '', i)
                info += i
                info = re.sub('\s', '', info)
        except:
            return None

        if info != '':
            '''
                将新闻存储到资料库中, 如果资料库
                mysql资料库,需要敲以下指令, mysql相关参数需要在conf.settings中配置
                create database news;
                use news;
                create table new1(
                    id int auto_increment,
                    primary key(id),
                    title varchar(100),
                    website varchar(100),
                    content text)default charset=utf8;
                create table word(
                    id int auto_increment,
                    primary key(id),
                    title varchar(100),
                    word varchar(100))default charset=utf8;
            '''
            sql = 'insert into new (website, title, content) VALUES (%s, %s, %s)'
            param = (newWebsite, newsTitle, info)
            db = SqlUtile()
            db.insert(sql=sql, params=param)
            topWord = part(info, newsTitle)
            # print(object_list)
            sql = 'insert into word (word, title) VALUES (%s, %s)'
            param = (topWord, newsTitle)
            db.insert(sql=sql, params=param)
            # time.sleep(3)

'''
    爬虫爬取的所有逻辑
'''
def spider_process():
    spider = opinionAnalysis()
    # 组合链接
    for url in URLS:
        html = spider.crawlPage(url)
        if html != '':
            spider.crawlNewsWebsite(html)

if __name__ == '__main__':
    spider_process()

logger.removeHandler(fileHandler)