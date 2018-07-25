
# -*- coding: utf-8 -*-
# BOT_NAME = ['sina', 'sina_fans']
BOT_NAME = ['sina']
# COMMANDS_MODULE = 'sina.commands'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# 使用scrapy_redis去重组件，不适用scrapy默认去重
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 使用scrapy-redis里的调度器组件，不适用scrapy默认的调度器组件
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 项目可以中途停止，允许暂停，redis请求记录不丢失
SCHEDULER_PERSIST = True

# 指定数据库的直接IP和端口号
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'

SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"

DOWNLOAD_DELAY = 2
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'sina.middlewares.SinaSpiderMiddleware': 543,
# }

DOWNLOADER_MIDDLEWARES = {
    'sina.middlewares.SinaUseAgentChange' : 300,
    'sina.middlewares.SinaCookieChange' : 301,
    'sina.middlewares.SinaDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
    'sina.pipelines.SinaPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Mysql参数配置
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DB = 'sina'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '12321hjz'

# 爬虫日志设置
LOG_FILE = 'SinaSpider.log'
LOG_LEVEL = 'INFO'

# 用户的信息
ACCOUNT_POOL = [
    # {'user': '13113121202', 'pwd': '12321hjz'},
    {'user': '0066970202729', 'pwd': 'bingo520'},
    {'user': '0013203357052', 'pwd': 'fa331595'},
    # {'user': '0013203357079', 'pwd': 'fa237181'},
    # {'user': '0013203357201', 'pwd': 'fa652193'},
    # {'user': '0013203357286', 'pwd': 'fa848138'},
]

# 云打码平台账号密码
YUN_USERNAME = 'Hjz59'
YUN_PASSWORD = '12321HJZ'



