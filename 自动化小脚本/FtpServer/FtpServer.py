# coding:utf-8
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import ThreadedFTPServer
import logging
import sys

logger = logging.getLogger('Logger')
formatter = logging.Formatter('%(message)s')
console_handler = logging.StreamHandler(sys.stdout)
# 终端日志按照指定的格式来写
console_handler.setFormatter(formatter)
# 可以设置日志的级别
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

class MyHandler(FTPHandler):
    def on_connect(self):
        logger.info("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        logger.info("%s:%s disconnect" % (self.remote_ip, self.remote_port))

    def on_login(self, username):
        # do something when user login
        logger.info("%s:%s login" % (self.remote_ip, self.remote_port))

    def on_logout(self, username):
        # do something when user logs out
        logger.info("%s:%s logout" % (self.remote_ip, self.remote_port))

    def on_file_sent(self, file):
        # do something when a file has been sent
        logger.info(file + ' senting....')

    def on_file_received(self, file):
        # do something when a file has been received
        logger.info(file + ' received')

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        logger.info(file + ' incomplete...........')

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)

def main():
    # 新建一个用户组
    authorizer = DummyAuthorizer()
    # 将用户名，密码，指定目录，权限 添加到里面
    authorizer.add_user("root", "123456", ".", perm="elradfmwMT")  # adfmw
    # 这个是添加匿名用户,任何人都可以访问，如果去掉的话，需要输入用户名和密码，可以自己尝试
    authorizer.add_anonymous(".")

    # 带宽限制
    dtp_handler = ThrottledDTPHandler
    dtp_handler.read_limit = 1024 * 1024  # 1M/sec (1024 * 1024)
    dtp_handler.write_limit = 1024 * 1024  # 1M/sec (1024 * 1024)

    # FTP初始参数设置
    handler = MyHandler
    handler.timeout = 300
    handler.authorizer = authorizer
    handler.banner = "Ftp Ready......"   # 进入欢迎语
    handler.dtp_handler = dtp_handler

    # 日志
    logging.basicConfig(filename='Ftp.log', level=logging.INFO)

    # 开启服务器
    server = ThreadedFTPServer(("0.0.0.0", 21), handler)
    server.max_cons = 500
    server.max_cons_per_ip = 10
    server.serve_forever()

if __name__ == '__main__':
    main()
logger.removeFilter(console_handler)