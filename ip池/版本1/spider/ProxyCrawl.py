from conf.settings import IPNUMBERS
from validator.check_db_ip import cheack_numbers
from spider.HtmlParse import start

class ProxyCrawl:
    def __init__(self, db_proxy_num):
        self.db_proxy_num = db_proxy_num
        self.db_proxy_num.value = cheack_numbers()

    def run(self):
        # print(self.db_proxy_num.value)
        if self.db_proxy_num.value < IPNUMBERS:
            print('excuse me')
            start(self.db_proxy_num.value)

def startProxyCrawl(db_proxy_num):
    crawl = ProxyCrawl(db_proxy_num)
    crawl.run()





