# 爬虫参数设置
MIN_WAIT_TIME = 30  # 爬虫获取网页失败，服务器端错误等待最小时间
MAX_WAIT_TIME = 60  # 爬虫获取网页失败，服务器端错误等待最大时间
NUM_RETRIES = 5  # 爬取错误最大上限尝试次数
THREADS_NUM = 2  # 线程池数量
MIN_PAGE = 1  # 爬虫页面设置，最小页面
MAX_PAGE = 50  # 爬虫页面设置，最大页面

# 响应状态码
STATUS_CODES = {
    'ok' : 200,
    'clientError':400,
    'severError': 500,
    'limit':600
}

# 查询新闻大类
URLS = ['https://news.baidu.com/guonei', 'https://news.baidu.com/guoji', 'https://news.baidu.com/mil',
        'https://news.baidu.com/finance', 'https://news.baidu.com/ent', 'https://news.baidu.com/sports',
        'https://news.baidu.com/internet', 'https://news.baidu.com/tech', 'https://news.baidu.com/game',
        'https://news.baidu.com/lady', 'https://news.baidu.com/auto', 'https://news.baidu.com/house']


# MYSQL连接池配置
DB_TEST_HOST="127.0.0.1"
DB_TEST_PORT=3306
DB_TEST_DBNAME="news"
DB_TEST_USER="root"
DB_TEST_PASSWORD="12321hjz"
DB_CHARSET="utf8" #数据库连接编码
DB_MIN_CACHED=10#mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
DB_MAX_CACHED=10#maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
DB_MAX_SHARED=20#maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
DB_MAX_CONNECYIONS=100#maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
DB_BLOCKING=True#blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
DB_MAX_USAGE=0#maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
DB_SET_SESSION=None#setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]


# 词云字体
FONT_PATH='C:/Users/Windows/fonts/simsun.ttc'