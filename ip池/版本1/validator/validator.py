'''检测IP是否可用'''
# from gevent import monkey;monkey.patch_all()
import requests
from conf.settings import VALIDATOR_TIMEOUT
from db.mongou import MongoUse
import gevent

def test_alive(proxy1, db_proxy_num):
    proxy = proxy1['ip'] + ':' + proxy1['port']
    if proxy1['protocol'] == 0:
        proxyformat = {'http' : proxy}
    elif proxy1['protocol']  == 1:
        proxyformat1 = {'https' : proxy}
    try:
        r = requests.get('http://www.ip138.com/',proxies=proxyformat, timeout = VALIDATOR_TIMEOUT)
        if r.status_code == 200:
            print('该代理IP：{}存活'.format(proxy))
            # db_proxy_num.value += 1
            outfile(proxy1)
    except:
        print('该代理{}失效'.format(proxy))
        return

def outfile(proxy1):
    mongou  = MongoUse()
    mongou.db_operat(operat='insert',sql=proxy1)

def start_valida(proxyes, db_proxy_num = 0):
    spawns = []
    for proxy in proxyes:
        # print(proxy)
        spawns.append(gevent.spawn(test_alive, proxy, db_proxy_num))
        gevent.joinall(spawns)


if __name__ == '__main__':
    proxyes = [{'ip': '115.218.218.168', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '115.223.247.140', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '114.234.80.254', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '121.232.199.165', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '115.223.215.196', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '61.145.194.26', 'port': '8080', 'type': 0, 'protocol': 0}, {'ip': '101.71.225.101', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '180.118.86.137', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '180.118.135.117', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '180.118.135.241', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '117.90.2.104', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '115.218.122.187', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '115.218.123.200', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '171.92.53.164', 'port': '9000', 'type': 0, 'protocol': 0}, {'ip': '121.232.148.118', 'port': '9000', 'type': 0, 'protocol': 0}]
    # # print(proxyes)
    # db_proxy_num = 0
    # spawns = []
    # for proxy in proxyes:
    #     # print(proxy)
    #     spawns.append(gevent.spawn(test_alive, proxy, db_proxy_num))
    #     gevent.joinall(spawns)
    start_valida(proxyes,0)
