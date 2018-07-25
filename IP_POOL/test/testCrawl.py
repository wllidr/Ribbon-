from lxml import etree
import requests
from conf.settings import parserList
import random

class Spider:
    def __init__(self, url):
        self.url = url

    def get_html(self):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
        self.r = requests.get(url = self.url, timeout = 20, headers = headers)
        self.text = self.r.text
        self.soup = etree.HTML(self.text)

    def get_infos(self):
        infos = self.soup.xpath("//table/tbody/tr")
        # print(infos)
        # print(infos[1].xpath('./td[2]/text()'))
        for info in infos:
            ip = info.xpath('./td[1]/text()')[0]
            port = info.xpath('./td[2]/text()')[0]
            type = info.xpath('./td[3]/text()')[0]
            protocol = info.xpath('./td[4]/text()')[0]
            print(ip, port, type, protocol)


if __name__ == '__main__':
    url = 'https://www.kuaidaili.com/free/'
    spider = Spider(url)
    spider.get_html()
    spider.get_infos()