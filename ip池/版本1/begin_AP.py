from multiprocessing import Queue, Process, Value, Array
from conf.settings import TASK_QUEUE_SIZE
from api.services_pool import startapi
from conf.settings import IPNUMBERS
from spider.ProxyCrawl import startProxyCrawl
import random

if __name__ == '__main__':
    DB_PROXY_NUM = Value('i', 0)   # 开辟共享内存
    # num2 = Array('b', range(IPNUMBERS))
    # fd1, fd2 = Pipe(False)   # 管道，fd1接收，fd2发送
    q1 = Queue(maxsize = TASK_QUEUE_SIZE)
    q2 = Queue()
    p1 = Process(target = startapi)  # 将搭建的服务器采用进程的方式打开
    p2 = Process(target = startProxyCrawl, args = (DB_PROXY_NUM,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(DB_PROXY_NUM)

