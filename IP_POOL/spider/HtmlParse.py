from lxml import etree
import requests
from conf.settings import parserList, PAGE_SCRATCH_TIMESLEEP
import random
from fake_useragent import UserAgent
import time
from multiprocessing import Pool
from validator.validator import start_valida


class Spider:
    def __init__(self, url, db_proxy_num):
        self.url = url
        self.db_proxy_num = db_proxy_num

    def get_html(self):
        ua = UserAgent()
        headers = {'user-agent': ua.random}
        self.r = requests.get(url = self.url, timeout = 20, headers = headers)
        self.text = self.r.text
        self.soup = etree.HTML(self.text)


    def get_infos(self, parser, url):
        infos = self.soup.xpath(parser['pattern'])
        # print(infos[1].xpath('./td[2]/text()'))
        htmlproxies = []
        for info in infos:
            ip = info.xpath(parser['position']['ip'])
            if len(ip) == 0:
                continue
            ip = ip[0]
            port = info.xpath(parser['position']['port'])[0]
            type = info.xpath(parser['position']['type'])[0]
            protocol = info.xpath(parser['position']['protocol'])[0]
            if type[0:2] == '高匿':
                type = 0
            else:
                type = 1
            if protocol == 'HTTP':
                protocol = 0
            elif protocol == 'HTTPS':
                protocol = 1
            sql = {'ip' : ip, 'port' : port, 'type' : type, 'protocol' : protocol, 'flag' : 0}
            htmlproxies.append(sql)
            # print(sql)

        if len(htmlproxies) > 0:
            print(htmlproxies)
            start_valida(htmlproxies, self.db_proxy_num)  # 爬取IP后直接进行验证
        # print(htmlproxies)
        # for proxy in htmlproxies:
        #     self.mongouse.db_operat(operat = 'insert', sql = proxy)

        # print(htmlproxies)
        # return htmlproxies

def scratch_process(url, parser, db_proxy_num):
    spider = Spider(url, db_proxy_num)
    spider.get_html()
    htmlproxies = spider.get_infos(parser, url)  # 返回一个页面捕获的多个IP
    time.sleep(PAGE_SCRATCH_TIMESLEEP)

def start(db_proxy_num):
    parser = random.choice(parserList)
    urls = parser['url']
    # print(urls)
    pool = Pool(processes = 1)
    for url in urls:
        # print(url)
        pool.apply_async(func = scratch_process, args = (url, parser, db_proxy_num))
    pool.close()
    pool.join()


if __name__ == '__main__':
    start(0)
