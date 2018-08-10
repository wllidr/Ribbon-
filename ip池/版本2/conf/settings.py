# 爬虫爬取网页以及正则
# PARSE_LIST = [{'urls' : ['https://www.cool-proxy.net/proxies/http_proxy_list/page:1'],'regular' : '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png" alt="Cn" /></td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?<td>([\s\S]*?)</'}]

PARSE_LIST = [
                {'urls' : ['http://www.89ip.cn/index_'+str(i)+'.html' for i in range(1, 45)], 'regular' : '<tr>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?<td>([\s\S]*?)</td'},
                # {'urls' : ['https://proxy.coderbusy.com/classical/https-ready.aspx?page=' + str(i) for i in range(1, 35)], 'regular' : '<td data-ip="([\s\S]*?)" data-i="[\s\S]*?" class="port-box">([\s\S]*?)</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?<td>([\s\S]*?)</td>'},
                {'urls':  ['http://www.xicidaili.com/wn/' + str(i) for i in range(1, 50)] + ['http://www.xicidaili.com/wt/' + str(i) for i in range(1, 50)],'regular': '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png" alt="Cn" /></td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?<td>([\s\S]*?)</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?<td>([\s\S]*?)</'},
                ]

# 爬虫获取网页失败，服务器端错误等待时间
MIN_WAIT_TIME = 30
MAX_WAIT_TIME = 60

# MYSQL连接池配置
DB_TEST_HOST="127.0.0.1"
DB_TEST_PORT=3306
DB_TEST_DBNAME="pool"
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

# MONGODB 配置
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'hjz'
MONGO_SHEET = 'ippool'

# 最小代理IP数量和最大代理IP数量
MIN_IP_NUMBERS = 50
MAX_IP_NUMBERS = 100

# 检测代理是否有用参数设置
TEST_PROXY_URL = 'http://uland.taobao.com/sem/tbsearch?refpid=mm_26632258_3504122_32538762&keyword=%E5%A5%B3%E8%A3%85&clk1=dc006e8965ac1e1ddef6aef0a77d951d&upsid=dc006e8965ac1e1ddef6aef0a77d951d'
TEST_PROXY_TIMEOUT = 10


