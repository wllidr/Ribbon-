#!/usr/bin/env python3
from threading import Thread
import socketserver, subprocess, sys
from pathlib import Path
from conf.settings import HTML_ROOT_DIR,IP,PORT,URLPATTERNS
import re
from aip_project.myaip import startaip
from httpserver.db.mysqlu import MysqlUse
from weather.seleniumUse import aduio_browser
from httpserver.db.mongouse import conveydata

class RequestHandler(socketserver.BaseRequestHandler):
    def sendOK(self):
        self.request.send('HTTP/1.0 200 OK\r\n'.encode('utf8'))

    def sendDenied(self):
        self.request.send('HTTP/1.0 403 Permission Denied\r\n'.encode('utf8'))

    def sendNF(self):
        self.request.send('HTTP/1.0 404 Not Found\r\n'.encode('utf8'))

    def sendContentType(self, file_path):
        extension = file_path.rsplit('.', 1)[1]
        if extension == 'html' or extension == 'htm':
            content_type = 'text/html'
        elif extension == 'png':
            content_type = 'image/png'
        elif extension == 'gif':
            content_type = 'image/gif'
        elif extension == 'jpeg' or extension == 'jpg':
            content_type = 'image/jpeg'
        elif extension == 'text' or extension == 'txt':
            content_type = 'text/plain'
        elif extension == 'css':
            content_type = 'text/css'
        elif extension == 'js':
            content_type = 'text/js'
        else:
            content_type = 'application/octet-stream'
        content_string = 'Content-Type: ' + content_type + '\r\n'
        self.request.send(content_string.encode('utf8'))

    def sendFile(self, contents):
        self.request.send(('Content-Length: ' + str(len(contents)) + '\r\n').encode('utf8'))
        self.request.send('Connection: close\r\n'.encode('utf8'))
        self.request.send('\r\n'.encode('utf8'))
        self.request.send(contents)

    def handleHTTP(self, text):
        sp = text.split('\r\n')
        if re.search('cityName', sp[-1]):
            # print(sp)
            unicodes = sp[-1].split('%5Cu')
            for i in range(len(unicodes)):
                unicodes[i] = '\\u' + unicodes[i]
            string = ''.join(unicodes)
            string1 = string.split('=')[1]
            string1 = string1.encode()
            # print(string1)
            logincity = string1.decode('unicode_escape')
            # print(logincity)
        request = sp[0].split(' ')
        filepath = '/' + request[1]
        if filepath[0] == '/' and filepath[1] == '/':
            filepath = filepath[1:]
            # print(filepath)

        temp = filepath.split('/')[1]
        temp = '/' + temp + '/'
        for url in URLPATTERNS:
            if temp == url[0] and (re.search('css', filepath) or re.search('image', filepath) or re.search('js', filepath) or re.search('video', filepath)):
                li = filepath.split('/')
                del li[0]
                del li[0]
                filepath = '/' + '/'.join(li)
                # print(filepath,1111111111)

        for url in URLPATTERNS:
            if filepath == url[0]:
                filepath = url[1]
        filepath = HTML_ROOT_DIR + filepath
        if request[0] == 'GET':
            if re.search('\?', filepath):
                # print(filepath)
                if re.search('Login', filepath):
                # 登陆验证账号密码,是否在数据库内
                    account = filepath.split('=')
                    pwd = account[2]
                    user = account[1].split('&')[0]
                    mquse = MysqlUse()
                    sql = 'select * from user where user = "%s" and pwd = "%s"' %(user, pwd)
                    data = mquse.fetch(sql)
                    print(data)
                    if len(data):
                        print('欢迎进入主界面')
                        filepath = 'httpserver/templates/static/index1LoginReturn.html'
                        myfile = Path(filepath)
                        if myfile.is_file():
                            with open(filepath, 'rb') as f:
                                # print("Sending " + filepath)
                                try:
                                    data = f.read()
                                    # print(data)
                                    self.sendOK()
                                    self.sendContentType(filepath)
                                    self.sendFile(data)
                                except:
                                    self.sendDenied()
                    else:
                        filepath = 'httpserver/templates/static/index.html'
                        myfile = Path(filepath)
                        if myfile.is_file():
                            with open(filepath, 'rb') as f:
                                # print("Sending " + filepath)
                                try:
                                    data = f.read()
                                    # print(data)
                                    self.sendOK()
                                    self.sendContentType(filepath)
                                    self.sendFile(data)
                                except:
                                    self.sendDenied()
                        print('User or Password Error')

                elif re.search('Register', filepath):
                # 注册，账号密码添加进入数据库
                    account = filepath.split('=')
                    pwd = account[3]
                    user = account[1].split('&')[0]
                    mquse = MysqlUse()
                    sql = 'select * from user where user = "%s"' % user
                    data = mquse.fetch(sql)
                    if data:
                        filepath = 'httpserver/templates/static/index.html'
                        myfile = Path(filepath)
                        if myfile.is_file():
                            with open(filepath, 'rb') as f:
                                # print("Sending " + filepath)
                                try:
                                    data = f.read()
                                    # print(data)
                                    self.sendOK()
                                    self.sendContentType(filepath)
                                    self.sendFile(data)
                                except:
                                    self.sendDenied()
                        print('有该账户密码，不允许注册')
                    else:
                        print(7777777)
                        sql = "insert into user (user, pwd) VALUES ('%s', '%s')" % (user, pwd)
                        mquse.excute(sql)
                        print('注册成功')
                        filepath = 'httpserver/templates/static/index3RegisterSu.html'
                        myfile = Path(filepath)
                        if myfile.is_file():
                            with open(filepath, 'rb') as f:
                                # print("Sending " + filepath)
                                try:
                                    data = f.read()
                                    # print(data)
                                    self.sendOK()
                                    self.sendContentType(filepath)
                                    self.sendFile(data)
                                except:
                                    self.sendDenied()

            else:
                myfile = Path(filepath)
                # print(filepath,66666666666)
                if myfile.is_file():
                    with open(filepath, 'rb') as f:
                        # print("Sending " + filepath)
                        try:
                            data = f.read()
                            # print(data)
                            self.sendOK()
                            self.sendContentType(filepath)
                            self.sendFile(data)
                        except:
                            self.sendDenied()
                else:
                    print("Sending 404, can't find " + filepath)
                    self.sendNF()

        elif request[0] == 'POST':
            if re.search('Voice', filepath):
            # 语音识别获取城市名称，selenium模拟浏览器进入网页中获取当前天气信息
                city = startaip()
                aduio_browser(city)
            elif re.search('Request', filepath):
                data = conveydata(logincity)
                self.sendOK()
                self.sendFile(data.encode())
                print(data)

        else:
            self.sendNF()
        self.request.close()

    def handle(self):
        data = self.request.recv(1024)
        text = data.decode()
        self.handleHTTP(text.strip())


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address):
        socketserver.TCPServer.__init__(self, server_address, RequestHandler)

def webstart():
    server = Server((IP, PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

