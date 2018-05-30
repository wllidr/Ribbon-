'''
使用套接字的方式搭建简单的HTTP服务器
'''
from socket import *
from conf.settings import IP,PORT
from multiprocessing import Process
from dict_operat.login import login
from dict_operat.register import register
from dict_operat.find import findhistory,findword
import signal
__author__ = 'Ribbon Huang'

def startapi():
    s = Services()
    s.serverForever()

class Services:
    def __init__(self):
        # 套接字的初始化设置
        ADDR = (IP, PORT)
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s.bind(ADDR)
        self.s.listen(5)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    def serverForever(self):
        # 用于提供浏览器客户端连接线程，起持续监听的效果
        while True:
            self.conn, self.addr = self.s.accept()
            p = Process(target=self.handle)
            p.start()

    def handle(self):
        while True:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                # print(data.decode())
                l = data.decode().split('_')
                if l[0] == 'L':
                    flag = login(l[1],l[2])
                    self.conn.send(flag.encode())
                    self.apphandle(l[1])
                elif l[0] =='R':
                    flag = register(l[1],l[2])
                    self.conn.send(flag.encode())
                else:
                    self.conn.send('格式有问题'.encode())

    def apphandle(self, name):
        while True:
            data = self.conn.recv(1024)
            if data.decode() == '2':
                data = findhistory()
                self.conn.send(data.encode())
            elif data.decode() == '1':
                self.conn.send('发送单词过来'.encode())
                while True:
                    word = self.conn.recv(1024)
                    if word.decode() == 'QUIT':
                        break
                    data = findword(word=word.decode(), name = name)
                    self.conn.send(data.encode())
            elif data.decode() == '3':
                break

if __name__ == '__main__':
    s = Services()
    s.serverForever()






