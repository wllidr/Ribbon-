'''
    协程方式进行验证IP是否可用
    由于协程的方式无法和celery搭配使用，所以改为使用线程池，两种方式都有进行保留
    Auhtor : Ribbon Huang
    Date : 2018-07-27
'''
# import gevent.monkey;gevent.monkey.patch_all()
# import gevent
import threadpool
import logging
import requests
from util.sqlUtil import SqlUtile
from util import redisuse
from conf.settings import TEST_PROXY_URL, TEST_PROXY_TIMEOUT

'''
    记录日常日志
'''
logger = logging.getLogger('spiderError')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler = logging.FileHandler('spiderError.log')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)
db = SqlUtile()
'''
    检测IP是否可用
'''
def test_alive(ip):
    proxy =ip['type'].lower() + r'://'+ip['ip'] + ':' + ip['port']
    if ip['type'] == 'HTTP':
        proxyformat = {'http' : proxy}
    elif ip['type']  == 'HTTPS':
        proxyformat = {'https' : proxy}
    try:
        r = requests.get(TEST_PROXY_URL, proxies = proxyformat, timeout = TEST_PROXY_TIMEOUT)
        if r.status_code == 200:
            print('该代理IP：{}存活'.format(proxy))
            load_database(ip)
    except:
        # print('该代理{}失效'.format(proxy))
        logger.warning(ip['ip'] + 'is void')

'''
    测试可用IP通过资料库
'''
def load_database(ip):
    sql = 'INSERT INTO useip (ip, port, type) VALUES (%s, %s, %s)'
    db.addTest(sql, ip)

'''
    测试启动调用项
'''
def start_valida(ips):
    # 线程池
    pool = threadpool.ThreadPool(10)
    requests = threadpool.makeRequests(test_alive, ips)
    [pool.putRequest(req) for req in requests]
    pool.wait()

    # 协程
    # spawns = []
    # for ip in ips:
    #     # print(proxy)
    #     spawns.append(gevent.spawn(test_alive, ip))
    # gevent.joinall(spawns)
    # gevent.sleep(0)

if __name__ == '__main__':
    proxyes = [{'ip': '69.55.223.64', 'port': '41766', 'type': 'HTTP'}, {'ip': '185.144.64.118', 'port': '8080', 'type': 'HTTP'}, {'ip': '213.125.130.220', 'port': '8090', 'type': 'HTTP'}, {'ip': '87.207.54.164', 'port': '8080', 'type': 'HTTP'}, {'ip': '171.100.9.150', 'port': '8080', 'type': 'HTTP'}, {'ip': '180.253.134.179', 'port': '8080', 'type': 'HTTP'}, {'ip': '27.147.146.138', 'port': '38157', 'type': 'HTTP'}, {'ip': '42.115.26.154', 'port': '8080', 'type': 'HTTP'}, {'ip': '190.2.142.22', 'port': '1080', 'type': 'HTTP'}, {'ip': '46.99.146.204', 'port': '53281', 'type': 'HTTP'}, {'ip': '5.189.28.135', 'port': '53281', 'type': 'HTTP'}, {'ip': '103.216.82.199', 'port': '6666', 'type': 'HTTP'}, {'ip': '180.183.47.196', 'port': '8080', 'type': 'HTTP'}, {'ip': '75.108.123.165', 'port': '44552', 'type': 'HTTP'}, {'ip': '189.17.22.185', 'port': '20183', 'type': 'HTTP'}]
    start_valida(proxyes)

logger.removeHandler(fileHandler)