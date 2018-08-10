'''
使用套接字的方式搭建简单的HTTP服务器，用于显示当前可用IP列表
'''
from socket import *
from conf.settings import IP,PORT
from threading import Thread
from validator.check_db_ip import cheack_ip_datas
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

    def serverForever(self):
        # 用于提供浏览器客户端连接线程，起持续监听的效果
        while True:
            self.conn, self.addr = self.s.accept()
            t = Thread(target=self.handle)
            t.start()

    def handle(self):
        # 用于将IP列表POST到浏览器上
        try:
            data = self.conn.recv(2048)
            requestHeaders = data.splitlines()
            for line in requestHeaders:
                print(line)
            Headers = "HTTP/1.1 200 OK\r\n"
            serverHeaders = [
                ('Content-Type', 'text/plain;charset=UTF-8'),
                ('Date', '2018-05-26'),
                ('Server', 'HTTPServer 1.0')
            ]

            for header in serverHeaders:
                Headers += "{0}:{1}\r\n".format(*header)
            Headers += '\r\n'
            datas = cheack_ip_datas()
            Body = ''
            for data in datas:
                data = '{' + data[1] + ':' + str(data[2]) + '}' + ' '
                Body += data
            response = Headers + Body
            self.conn.send(response.encode())
            self.conn.close()
        except:
            pass

if __name__ == '__main__':
    s = Services()
    s.serverForever()






