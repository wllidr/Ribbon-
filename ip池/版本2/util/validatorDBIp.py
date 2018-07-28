'''
    协程方式进行验证原先可用IP是否还一直可用，不可用则剔除.
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
            pass
            print('该代理IP：{}存活'.format(proxy))
    except:
        print('该代理{}失效'.format(proxy))
        update_database(ip)
        logger.warning(ip['ip'] + ' is void')

'''
    测试可用IP通过资料库
'''
def update_database(ip):
    sql = 'UPDATE useip SET  isuse=0 where id=%s'
    db.updateIp(sql, ip)

'''
    测试启动调用项
'''
def start_valida():
    # 资料库提取原先可用IP
    ips = []
    sql = 'SELECT * FROM useip'
    datas = db.fetchAllData(sql)
    # print(datas)
    for data in datas:
        ips.append({'id':data[0],'ip': data[1].decode('utf8'), 'port': data[2].decode('utf8'), 'type': data[3].decode('utf8')})
    # print(ips)
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

if __name__ == '__main__':
    start_valida()

logger.removeHandler(fileHandler)