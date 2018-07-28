# 获取 http://www.xicidaili.com 代理IP的爬虫所需配置
parserList = [
    {
        'url' : ['http://www.xicidaili.com/nn/%s' %(str(n)) for n in range(1,3)] + ['http://www.xicidaili.com/nt/%s' %(str(n)) for n in range(1,1)],
        'pattern' : "//table[@id='ip_list']//tr",
        'position': {'ip': './td[2]/text()', 'port': './td[3]/text()', 'type': './td[5]/text()', 'protocol': './td[6]/text()'}
    },
    {
        'url' : ['https://www.kuaidaili.com/free/inha/%s' %(str(n)) for n in range(1,5)],
        'pattern' : "//table/tbody/tr",
        'position': {'ip': './td[1]/text()', 'port': './td[2]/text()', 'type': './td[3]/text()', 'protocol': './td[4]/text()'}
    },
    # {
    #
    # }
]

# 套接字参数
IP = '127.0.0.1'
PORT = 8000

# MYSQL 配置
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'hjz'
MYSQL_USER = 'root'
MYSQL_PASSWD = '12321hjz'

# MONGODB 配置
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'hjz'
MONGO_SHEET = 'ippool'

PAGE_SCRATCH_TIMESLEEP = 5 # 爬取每一个界面所需要的休眠时间
IPNUMBERS = 100  # IP的上限下限
TASK_QUEUE_SIZE = 5  # 启动进程中队列数目
MAX_DOWNLOAD_CONCURRENT = 3  # 从免费代理网站下载时的最大并发
CHECK_WATI_TIME = 1  # 进程数达到上限时的等待时间
VALIDATOR_TIMEOUT = 5  # 验证IP是否有用延迟时间
THREADNUM = 5


