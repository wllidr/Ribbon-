'''
    Date : 2018 - 11 - 27
    Author :Ribbon Huang
    Desc:
        平安自动巡检报告自动生成。
'''
# import gevent.monkey;gevent.monkey.patch_all()
# import gevent
import pandas as pd
import time
import paramiko
import re
import threadpool
import xlwt
from functools import partial
import datetime
import logging
import schedule
import os
import xlrd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 获取logger的实例
logger = logging.getLogger("pingAnLogger")
formatter = logging.Formatter('%(asctime)s____%(message)s')
file_handler = logging.FileHandler("平安自动巡检日志.txt")
file_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

j = 2
scriptLine = {}
backUser = 'pawlan'
backPassword = 'Pawlan@2018'

# 设置居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
font = xlwt.Font()  # 为样式创建字体
# 设置字体颜色
font.colour_index = 'red'
style = xlwt.XFStyle()  # Create the Pattern
style.alignment = alignment

class EmailSend:
    def __init__(self, Sender, Password, SMPTsever):
        self.SMPTsever = SMPTsever
        self.Sender = Sender
        self.Password = Password

    def mailcontent(self, Message, Subject, To, filename, Cc):
        self.msg =  MIMEMultipart()
        xlsxpart = MIMEApplication(open(filename, 'rb').read())
        xlsxpart.add_header('Content-Disposition', 'attachment', filename='ChinaPingAnLifeDutyReport_' + re.sub('点','', filename.split('总表')[-1]))
        self.msg.attach(xlsxpart)

        # 添加文本内容
        text_msg = MIMEText(Message, 'plain', 'utf-8')
        self.msg.attach(text_msg)

        # 邮件标题以及发送的对象以及抄送对象
        self.msg['Subject'] = Subject
        self.msg['From'] = self.Sender
        self.msg['To'] = self.To = To
        self.Cc = Cc
        self.msg['Cc'] = Cc

    def sendmail(self, port):
        try:
            self.server = smtplib.SMTP(self.SMPTsever, port)   # 587 465
            self.server.starttls()
            self.server.login(self.Sender, self.Password)
            self.server.sendmail(self.Sender, self.To.split(';') + self.Cc.split(';'), self.msg.as_string())
        except Exception as e:
            print(e)

    def quitemail(self):
        self.server.quit()

def begin_send_email(filename):
    # 从文件中提取收件人，发件人以及抄送人
    try:
        info = [[], [], []]
        with open('值守邮箱.txt', 'rb') as f :
            i = 0
            for line in f:
                line = line.decode('gbk', 'ignore')
                if re.search('收件', line) or re.search('抄送', line):
                    i += 1
                else:
                    if not re.search('发件', line) and line.strip() != '':
                        if line.strip()[-1] == ';':
                            info[i].append(line.strip())
                        else:
                            info[i].append(line.strip() + ';')
    except:
        return

    if info[0] and info[1]:
        # 账号密码信息
        sender = info[0][0][:-1]
        password = info[0][-1][:-1]
        # 邮件所需相关参数
        subject = os.path.basename(filename).split('.')[0]
        message = '各位老师好：\n\t      附件为' + subject + ',请查阅。'
        messageto = ''.join(info[1])
        messageto = messageto.strip()[:-1]

        try:
            cc = "".join(info[2])
        except:
            cc = ''
        # cc = ''
        port = 587
        smptsever = 'smtpcn01.huawei.com'
            # print(cc)
            # print(messageto)
            # # 邮件发送所有流程
        try:
            email = EmailSend(sender, password, smptsever)
            email.mailcontent(message, subject, messageto, filename, cc)
            email.sendmail(port=port)
            email.quitemail()
            print('发送成功，并且成功退出Email,欢迎下次使用，谢谢！')
        except:
            pass

class StelnetError(Exception):
    '''自定义的错误'''
    def __init__(self,ErrorInfo):
        super().__init__(self)
        #初始化父类
        self.errorinfo=ErrorInfo

    def __str__(self):
        return self.errorinfo

class MySSH:
    def __init__(self, host, port, username, passwd, device_name, worksheet, workclass, workpeople):
        self.worksheet = worksheet
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.device_name = device_name
        self.ssh_fd = None
        self.workclass = workclass
        self.workpeople = workpeople

        # 红色字体
        alignment1 = xlwt.Alignment()
        alignment1.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
        alignment1.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
        font = xlwt.Font()  # 为样式创建字体
        font.colour_index = 10
        self.fontStyle1 = xlwt.XFStyle()  # Create the Pattern
        self.fontStyle1.alignment = alignment
        self.fontStyle1.font = font

    def ssh_connect(self):
        self.ssh_fd = paramiko.SSHClient()
        self.ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_fd.connect(self.host, port = self.port, username = self.username, password = self.password)
        self.channel = self.ssh_fd.invoke_shell()
        self.channel.timeout = 30
        self.channel.settimeout(30)
        self.channel.keep_this = self.ssh_fd


    def exe(self, cmd):
        '''有验证执行shell'''
        self.channel.send(cmd)
        time.sleep(0.5)
        info = ''
        while True:
            if cmd.strip() == self.password:
                break
            if cmd.strip() == backPassword:
                break
            temp = self.channel.recv(30000)
            try:
                info = info + temp.decode('utf8', 'ignore')
            except:
                break
            info = re.sub('\\x1b\[\d*\w?', '', info)
            info = re.sub('\r\n', '\n', info)
            if cmd.strip().replace(' ', '') in info.replace(' ', ''):
                break
            elif 'password' in info.lower() or re.search('\[\w.*?\]', info):
                break
            else:
                time.sleep(3)
        print(info)
        return info

    def stelnet(self, ip, username, password, port):
        # 使用life2018登录
        print('连接' + ip + ' ' + str(port) + '使用主账号密码...........')
        self.exe('sys' + '\n')
        info = self.exe('stelnet ' + ip + ' ' +str(port) + '\n')
        if re.search('inputtheusername', re.sub(' ', '', info)):
            info = self.exe(username + '\n')
            time.sleep(5)
        else:
            time.sleep(8)
            self.exe(username + '\n')
        timep = 1
        while True:
            if timep == 4:
                return True
            if re.search('publickey\?\[Y/N]', re.sub(' ', '', info)):
                info = self.exe('n' + '\n')
            elif re.search('Continuetoaccessit\?\[Y/N]', re.sub(' ', '', info)):
                info = self.exe('y' + '\n')
            elif re.search('Enterpassword', re.sub(' ', '', info)):
                info = self.exe(password + '\n')
                times = 1
                while times < 4:
                    if re.search('Enterpassword', re.sub(' ', '', info)):
                        info = self.exe(password + '\n')
                    if times == 3:
                        info = self.exe('#\n')
                        if re.search('Theconnectionwasclosedbytheremotehost', re.sub(' ', '', info)):
                            self.stelnetback(ip, backUser, backPassword, port)
                    times += 1
                break
            elif re.search('Theconnectionwasclosedbytheremotehost', re.sub(' ', '', info)):
                self.stelnetback(ip, backUser, backPassword, port)
                break
            else:
                time.sleep(10)
                info = self.exe('y' + '\n')
                timep += 1

    def stelnetback(self, ip, username, password, port):
        # 使用pawlan做登录
        print('连接' + ip + ' ' +str(port) + '使用备份账号密码...........')
        info = self.exe('stelnet ' + ip + ' ' +str(port) + '\n')
        if re.search('inputtheusername', re.sub(' ', '', info)):
            info = self.exe(username + '\n')
            time.sleep(5)
        else:
            time.sleep(10)
            self.exe(username + '\n')
        times3 = 1
        while times3 < 4:
            if re.search('publickey\?\[Y/N]', re.sub(' ', '', info)):
                info = self.exe('n' + '\n')
            elif re.search('Continuetoaccessit\?\[Y/N]', re.sub(' ', '', info)):
                info = self.exe('y' + '\n')
            elif re.search('Enterpassword', re.sub(' ', '', info)):
                info = self.exe(password + '\n')
                break
            elif re.search('Theconnectionwasclosedbytheremotehost', re.sub(' ', '', info)):
                break
            else:
                time.sleep(10)
                info = self.exe('y' + '\n')
            times3 += 1

    def AR1(self, devicename):
        # 只有一台路由器的情况
        ar1 = {}
        self.exe('scr 0 t\n')
        utilization = self.utilization()
        if utilization:
            ar1['上行'] = utilization[0].strip()
            ar1['下行'] = utilization[0].strip()
        cpu = self.cpuUse()
        if cpu:
            ar1['control'] = cpu[0].strip()
            ar1['data'] = cpu[1].strip()
        memory = self.memoryUse()
        if memory:
            ar1['mem-usage'] = memory.strip()
        used = self.used(devicename)
        return ar1, used

    def AR12(self, arIp, ar1Or2, downOrUp, deviceName):
        '''获取AR1, AR2参数逻辑， 以及用户使用数逻辑'''
        ar1 = ar2  =None
        used = 'used'
        print('进入AR12')
        print(arIp, ar1Or2, downOrUp)
        if ar1Or2 == 1:
            ar1 = {'上行': '--', '下行': '--', 'control': '--', 'data': '--', 'mem-usage': '--'}
            utilization = self.utilization()
            if utilization:
                ar1['上行'] = utilization[0].strip()
                ar1['下行'] = utilization[0].strip()
            cpu = self.cpuUse()
            if cpu:
                ar1['control'] = cpu[0].strip()
                ar1['data'] = cpu[1].strip()
            memory = self.memoryUse()
            if memory:
                ar1['mem-usage'] = memory.strip()
            used = self.used(deviceName)
        elif ar1Or2 == 2:
            ar2 = {'上行': '--', '下行': '--', 'control': '--', 'data': '--', 'mem-usage': '--'}
            utilization = self.utilization()
            if utilization:
                ar2['上行'] = utilization[0].strip()
                ar2['下行'] = utilization[0].strip()
            cpu = self.cpuUse()
            if cpu:
                ar2['control'] = cpu[0].strip()
                ar2['data'] = cpu[1].strip()
            memory = self.memoryUse()
            if memory:
                ar2['mem-usage'] = memory.strip()

        if not ar1 :
            # 补齐ar1
            used = self.used(deviceName)
            ar1 = {'上行': '--', '下行': '--', 'control': '--', 'data': '--', 'mem-usage': '--'}
            if downOrUp.lower() == 'up':
                print('补齐ar1')
                ar1 = {}
                arIp = arIp.split('.')
                arIp = '.'.join(arIp[0: -1]) + '.' + str(int(arIp[-1]) - 1)
                flagy = self.stelnet(arIp, self.username, self.password, port=self.port)
                if not flagy:
                    self.exe('n\n')
                    print('进入第二层')
                    self.exe('scr 0 t\n')
                    utilization = self.utilization()
                    if utilization:
                        ar1['上行'] = utilization[0].strip()
                        ar1['下行'] = utilization[0].strip()
                    cpu = self.cpuUse()
                    if cpu:
                        ar1['control'] = cpu[0].strip()
                        ar1['data'] = cpu[1].strip()
                    memory = self.memoryUse()
                    if memory:
                        ar1['mem-usage'] = memory.strip()
                else:
                    ar1['mem-usage'] = '！'
                    ar1['control'] = '！'
                    ar1['data'] = '！'
                    ar1['上行'] = '！'
                    ar1['下行'] = '！'
            else:
                ar1['mem-usage'] = 'Down'
                ar1['control'] = 'Down'
                ar1['data'] = 'Down'
                ar1['上行'] = 'Down'
                ar1['下行'] = 'Down'
        else:
            #  补齐ar2
            ar2 = {'上行': '--', '下行': '--', 'control': '--', 'data': '--', 'mem-usage': '--'}
            if downOrUp.lower() == 'up':
                print('补齐ar2')
                ar2 = {}
                arIp = arIp.split('.')
                if '内蒙古诚信营业区' in self.device_name.strip():
                    arIp = '.'.join(arIp[0: -1]) + '.' + str(int(arIp[-1]) - 1)
                else:
                    arIp = '.'.join(arIp[0: -1]) + '.' + str(int(arIp[-1]) + 1)
                flagy = self.stelnet(arIp, self.username, self.password, port=self.port)
                if not flagy:
                    self.exe('n\n')
                    print('进入第二层')
                    self.exe('scr 0 t\n')
                    utilization = self.utilization()
                    if utilization:
                        ar2['上行'] = utilization[0].strip()
                        ar2['下行'] = utilization[0].strip()
                    cpu = self.cpuUse()
                    if cpu:
                        ar2['control'] = cpu[0].strip()
                        ar2['data'] = cpu[1].strip()
                    memory = self.memoryUse()
                    if memory:
                        ar2['mem-usage'] = memory.strip()
                else:
                    ar2['mem-usage'] = '！'
                    ar2['control'] = '！'
                    ar2['data'] = '！'
                    ar2['上行'] = '！'
                    ar2['下行'] = '！'
            else:
                ar2['mem-usage'] = 'Down'
                ar2['control'] = 'Down'
                ar2['data'] = 'Down'
                ar2['上行'] = 'Down'
                ar2['下行'] = 'Down'
        if used == 'used':
            used = self.used(deviceName)
        return ar1, ar2, used

    def get_excel_infos(self):
        '''表格写入获取的参数'''
        global j
        global style
        # 年月日时分

        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().month)
        day = str(datetime.datetime.now().day)
        hour = str(datetime.datetime.now().hour)
        minute = str(datetime.datetime.now().minute)

        self.exe('scr 0 t\n')
        info = self.exe('display  current-configuration  |  include  sysname\n') + self.exe('#\n')
        # print(info)
        ar1Or12 = re.findall('sysname([\s\S]*?)\n', info)[-1].strip()
        deviceNametemp = ar1Or12
        ar1Or12 = ar1Or12.split('-')[-1].split('_')[-1]
        if self.workclass.strip().lower() == 'e':
            # 只有一台路由器的情况
            print('只有一台路由器的情况')
            ar1,used = self.AR1(deviceNametemp)
            if ar1 and used:
                self.worksheet.write(j, 0, year + '年' + month + '月' + day + '日' + hour + '时' + minute + '分', style)
                self.worksheet.write(j, 1, self.device_name, style)
                self.worksheet.write(j, 2, self.host, style)
                self.worksheet.write(j, 3, self.workclass, style)
                self.worksheet.write(j, 4, self.workpeople, style)
                self.worksheet.write(j, 5, used, style)
                if ar1['control'] == '！' or ar1['control'] == 'Down':
                    self.worksheet.write(j, 6, ar1['control'], self.fontStyle1)
                    self.worksheet.write(j, 7, ar1['data'], self.fontStyle1)
                    self.worksheet.write(j, 8, ar1['mem-usage'], self.fontStyle1)
                    self.worksheet.write(j, 9, ar1['上行'], self.fontStyle1)
                    self.worksheet.write(j, 10, ar1['下行'], self.fontStyle1)
                else:
                    self.worksheet.write(j, 6, ar1['control'], style)
                    self.worksheet.write(j, 7, ar1['data'], style)
                    self.worksheet.write(j, 8, ar1['mem-usage'], style)
                    if ar1['上行'] == '0.00%':
                        self.worksheet.write(j, 9, ar1['上行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 9, ar1['上行'], style)
                    if ar1['下行'] == '0.00%':
                        self.worksheet.write(j, 10, ar1['下行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 10, ar1['下行'], style)
                self.worksheet.write(j, 11, '--', style)
                self.worksheet.write(j, 12, '--', style)
                self.worksheet.write(j, 13, '--', style)
                self.worksheet.write(j, 14, '--', style)
                self.worksheet.write(j, 15, '--', style)
                print('over', j - 1)
                if j % 30 == 0:
                    j += 2
                j += 1
            else:
                print('不全ar1', ar1, used)
        else:
            print('两台路由器的情况')
            info = self.exe('dis ip interface brief ' + '\n').lower() + self.exe('#' + '\n').lower()
            # print(info)
            ar2Ip = None
            if self.workclass.strip().lower() == 'a':
                # 两台路由器的情况
                if re.search('gigabitethernet0/0/4\.4001([\s\S]*?)/', info):
                    ar2Ip = re.search('gigabitethernet0/0/4\.4001([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n', info.lower()).groups()
                    downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                    ar2Ip = ar2Ip[0].strip()
                elif re.search('gigabitethernet0/0/4([\s\S]*?)/', info.lower()):
                    ar2Ip = re.search('gigabitethernet0/0/4([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n', info.lower()).groups()
                    # print(ar2Ip)
                    downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                    ar2Ip = ar2Ip[0].strip()
                if not ar2Ip:
                    print('找不到')
                    if re.search('gigabitethernet0/0/0\.4001([\s\S]*?)/', info):
                        ar2Ip = re.search('gigabitethernet0/0/0\.4001([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n',
                                          info.lower()).groups()
                        downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                        ar2Ip = ar2Ip[0].strip()
                    elif re.search('gigabitethernet0/0/0([\s\S]*?)/', info):
                        ar2Ip = re.search('gigabitethernet0/0/0([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n',
                                          info.lower()).groups()
                        downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                        ar2Ip = ar2Ip[0].strip()
            else:
                if re.search('gigabitethernet0/0/0\.4001([\s\S]*?)/', info):
                    ar2Ip = re.search('gigabitethernet0/0/0\.4001([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n',
                                      info.lower()).groups()
                    downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                    ar2Ip = ar2Ip[0].strip()
                elif re.search('gigabitethernet0/0/0([\s\S]*?)/', info):
                    ar2Ip = re.search('gigabitethernet0/0/0([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n', info.lower()).groups()
                    downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                    ar2Ip = ar2Ip[0].strip()
                if not ar2Ip:
                    if re.search('gigabitethernet0/0/4\.4001([\s\S]*?)/', info):
                        ar2Ip = re.search('gigabitethernet0/0/4\.4001([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n',
                                          info.lower()).groups()
                        downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                        ar2Ip = ar2Ip[0].strip()
                    elif re.search('gigabitethernet0/0/4([\s\S]*?)/', info.lower()):
                        ar2Ip = re.search('gigabitethernet0/0/4([\s\S]*?)/\d*? ([\s\S]*?) [a-z]*?\n',
                                          info.lower()).groups()
                        # print(ar2Ip)
                        downOrUp = [d for d in ar2Ip[-1].split(' ') if d != ''][0]
                        ar2Ip = ar2Ip[0].strip()
            ar1, ar2, used = self.AR12(ar2Ip, int(ar1Or12), downOrUp, deviceNametemp)
            time.sleep(1)
            if ar1 and ar2 and used:
                self.worksheet.write(j, 0, year + '年' + month + '月' + day + '日' + hour + '时' + minute + '分', style)
                self.worksheet.write(j, 1, self.device_name, style)
                self.worksheet.write(j, 2, self.host, style)
                self.worksheet.write(j, 3, self.workclass, style)
                self.worksheet.write(j, 4, self.workpeople, style)
                self.worksheet.write(j, 5, used, style)
                if ar1['control'] == '！' or ar1['control'] == 'Down':
                    self.worksheet.write(j, 6, ar1['control'], self.fontStyle1)
                    self.worksheet.write(j, 7, ar1['data'], self.fontStyle1)
                    self.worksheet.write(j, 8, ar1['mem-usage'], self.fontStyle1)
                    self.worksheet.write(j, 9, ar1['上行'], self.fontStyle1)
                    self.worksheet.write(j, 10, ar1['下行'], self.fontStyle1)
                else:
                    self.worksheet.write(j, 6, ar1['control'], style)
                    self.worksheet.write(j, 7, ar1['data'], style)
                    self.worksheet.write(j, 8, ar1['mem-usage'], style)
                    if ar1['上行'] == '0%':
                        self.worksheet.write(j, 9, ar1['上行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 9, ar1['上行'], style)
                    if ar1['下行'] == '0%':
                        self.worksheet.write(j, 10, ar1['下行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 10, ar1['下行'], style)
                if ar2['control'] == '！' or ar2['control'] == 'Down':
                    self.worksheet.write(j, 11, ar2['control'], self.fontStyle1)
                    self.worksheet.write(j, 12, ar2['data'], self.fontStyle1)
                    self.worksheet.write(j, 13, ar2['mem-usage'], self.fontStyle1)
                    self.worksheet.write(j, 14, ar2['上行'], self.fontStyle1)
                    self.worksheet.write(j, 15, ar2['下行'], self.fontStyle1)
                else:
                    self.worksheet.write(j, 11, ar2['control'], style)
                    self.worksheet.write(j, 12, ar2['data'], style)
                    self.worksheet.write(j, 13, ar2['mem-usage'], style)
                    if ar2['上行'] == '0.00%':
                        self.worksheet.write(j, 14, ar2['上行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 14, ar2['上行'], style)
                    if ar2['下行'] == '0.00%':
                        self.worksheet.write(j, 15, ar2['下行'], self.fontStyle1)
                    else:
                        self.worksheet.write(j, 15, ar2['下行'], style)
                print('over', j - 1)
                if j % 30 == 0:
                    j += 2
                j += 1
            else:
                print('不全ar2', ar2, ar1, used)

    def used(self, deviceName):
        # used的获取， 以及所有获取参数表格写入
        print('获取用户数.....')
        used = ['--', '--', '--', '--', '--']
        info = self.exe('dis ip interface brief ' + '\n').lower() + self.exe('#' + '\n').lower()
        tempFlag = False
        for line in scriptLine['获取used']:
            if line.strip().split(' ')[-1].lower() in info:
                tempFlag = True
                break
        if tempFlag:
            # 有vlanif2 则可以直接获取used
            for line in scriptLine['获取used']:
                info = self.exe(line + '\n')
                info += self.exe('#\n')
                if re.search('notexist', re.sub(' ', '', info)):
                    if line == scriptLine['获取used'][-1]:
                        logger.warning(self.host.strip() + ' ' + self.device_name['设备名'].strip() + ' 五条语句都查找不到，请重新确定script.txt中命令')
                    continue
                else:
                    start = info.index('Used')
                    info = info[start: ]
                    used = [a for a in re.search('(133\.\d*?\.\d*?\.[\s\S]*?)\n', info).groups()[0].split(' ') if a!='']
                    break
        else:
            # print(info)
            temp = re.search('(133\.\d*?\.\d*?\.[\s\S]*?)/', info).groups()[0]
            temp = temp.split('.')
            ip = '.'.join(temp[0: -1]) + '.' + str(int(temp[-1]) - 1)
            self.stelnet(ip, self.username, self.password, port=55522)
            self.exe('n\n')
            info = self.exe('display  current-configuration  |  include  sysname\n') + self.exe('#\n')
            device = re.findall('sysname([\s\S]*?)\n', info)[-1].strip()
            if device != deviceName:
                info = self.exe('scr 0 t\n')
                for line in scriptLine['获取used']:
                    if re.search('\[', info) and re.search(']', info):
                        raise StelnetError('Stelnet ' + self.host + '错误')
                    info = self.exe(line + '\n') + self.exe('#\n')
                    if re.search('notexist', re.sub(' ', '', info)):
                        if line == scriptLine['获取used'][-1]:
                            logger.warning(self.host.strip() + ' ' + self.device_name.strip() + ' 五条语句都查找不到，请重新确定脚本文件中命令')
                        continue
                    else:
                        info += self.exe('#\n')
                        start = info.index('Used')
                        info = info[start: ]
                        used = [a for a in re.search('(133\.\d*?\.\d*?\.[\s\S]*?)\n', info).groups()[0].split(' ') if a != '']
                        self.exe('return\n')
                        self.exe('quit\n')
                        break
        return used[-4]

    def cpuUse(self):
        '''CPU control data两个参数获取'''
        print('获取CPU的参数.......')
        for line in scriptLine['获取CPU利用率']:
            info = self.exe(line + '\n')
            info += self.exe('#' + '\n')
            cpu = re.findall('CPU Usage: ([\s\S]*?)Max', info)
        return cpu

    def memoryUse(self):
        '''内存使用率的获取'''
        print('获取内存参数............')
        for line in scriptLine['获取内存利用率']:
            info = self.exe(line + '\n')
            info += self.exe('#' + '\n')
            memory = re.search('Memory Using Percentage Is:([\s\S]*?)\n', info).groups()[0]
        return memory

    def utilization(self):
        '''上行下行两个参数的获取'''
        print('获取上行下行参数...........')
        info = self.exe('display interface GigabitEthernet0/0/4 | include bandwidth\n') + self.exe('#\n')
        if re.search('Outputbandwidthutilization', re.sub(' ', '', info)) and re.search('Inputbandwidthutilization', re.sub(' ', '', info)):
            InputUtilization = re.search('Input bandwidth utilization  :([\s\S]*?)\n', info).groups()[0].strip()
            OuputUtilization = re.search('Output bandwidth utilization :([\s\S]*?)\n', info).groups()[0].strip()
            # print(InputUtilization, OuputUtilization)
            return [InputUtilization, OuputUtilization]
        info = self.exe('display interface GigabitEthernet0/0/1 | include bandwidth\n') + self.exe('#\n')
        if re.search('Outputbandwidthutilization', re.sub(' ', '', info)) and re.search('Inputbandwidthutilization', re.sub(' ', '', info)):
            InputUtilization = re.search('Input bandwidth utilization  :([\s\S]*?)\n', info).groups()[0].strip()
            OuputUtilization = re.search('Output bandwidth utilization :([\s\S]*?)\n', info).groups()[0].strip()
            # print(InputUtilization, OuputUtilization)
            return [InputUtilization, OuputUtilization]

    def close(self):
        '''SSH的关闭'''
        self.ssh_fd.close()

def read_csv():
    file = r'路由器参数.xls'
    df = pd.read_excel(file, header=None)
    df = df.dropna(axis=0, how='all')
    df = df.fillna(method='ffill', axis=0)
    # print(df)
    df = df.drop_duplicates(1, 'first')
    key = [str(i).strip() for i in df.iloc[0, :].tolist()]
    csv_infos = []
    df.index = [x for x in range(df.shape[0])]
    for i in range(1, df.shape[0]):
        temp = df.iloc[i, :].tolist()
        temp1 = {}
        for i in range(len(temp)):
            temp1[str(key[i])] = str(temp[i])
        csv_infos.append(temp1)
    return csv_infos

def main_process(worksheet, csv_info, retried = 2):
    device_name = csv_info['设备名']
    host = csv_info['设备IP']
    port = csv_info['设备端口号']
    username = csv_info['设备登录帐号']
    password = csv_info['设备登录密码']
    workClass = csv_info['职场类别']
    workPeople = csv_info['职场人数']
    if re.search('\.', host):
        ssh = MySSH(host=host, port=port, username=username, passwd=password, device_name=device_name, worksheet=worksheet, workclass=workClass, workpeople=workPeople)
        # ssh.ssh_connect()
        # ssh.get_excel_infos()
        try:
            ssh.ssh_connect()
            ssh.get_excel_infos()
        except Exception as e:
            if retried > 0:
                time.sleep(5)
                ssh.close()
                main_process(worksheet, csv_info, retried=retried-1)
            else:
                logger.warning(csv_info['设备IP'].strip() + ' ' + csv_info['设备名'].strip() + str(e).strip())
        finally:
            ssh.close()
    else:
        pass

def poolUse(poolNumber, worksheet, csv_infos):
    '''线程池启用主程序采集步骤'''
    start3 = time.time()
    fun1 = partial(main_process, worksheet)
    pool = threadpool.ThreadPool(poolNumber)
    requests = threadpool.makeRequests(fun1, csv_infos)
    [pool.putRequest(req) for req in requests]
    pool.wait()

    # 协程
    # spawns = []
    # for csv_info in csv_infos:
    #     spawns.append(gevent.spawn(fun1, csv_info))
    # gevent.joinall(spawns)
    end3 = time.time()
    print("本次职场巡检耗时: " + str(end3 - start3) + '秒')

def split_table(table_name, t):
    '''一个表格切割成4个表格'''
    file_path = table_name
    t = t.split('_')[-1]
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    nrows = sheet.nrows
    start = 0
    distance = end = int(nrows / 4)

    for pp in range(4):
        workbookback = xlwt.Workbook()
        worksheetback = workbookback.add_sheet('Sheet1')
        line = 2
        for cell in range(0, 16):
            worksheetback.col(cell).width = 0x0d00 + 50 * 50
        # 第一行参数
        worksheetback.write_merge(0, 1, 0, 0, '时间', style)
        worksheetback.write_merge(0, 1, 1, 1, '设备名称', style)
        worksheetback.write_merge(0, 1, 2, 2, 'IP', style)
        worksheetback.write_merge(0, 1, 3, 3, '职场类别', style)
        worksheetback.write_merge(0, 1, 4, 4, '职场人数', style)
        worksheetback.write_merge(0, 1, 5, 5, '用户数(VLAN2)', style)
        worksheetback.write_merge(0, 0, 6, 10, 'AR1', style)
        worksheetback.write(1, 6, 'control', style)
        worksheetback.write(1, 7, 'data', style)
        worksheetback.write(1, 8, 'mem-usage', style)
        worksheetback.write(1, 9, '上行', style)
        worksheetback.write(1, 10, '下行', style)
        worksheetback.write_merge(0, 0, 11, 15, 'AR2', style)
        worksheetback.write(1, 11, 'control', style)
        worksheetback.write(1, 12, 'data', style)
        worksheetback.write(1, 13, 'mem-usage', style)
        worksheetback.write(1, 14, '上行', style)
        worksheetback.write(1, 15, '下行', style)

        for i in range(start, end):
            try:
                info = sheet.row_values(i + 2)
                if info[0] != '':
                    # print(info)
                    for value in range(16):
                        worksheetback.write(line, value, info[value], style)
                    line += 1
            except:
                pass
        start = end
        end = end + distance
        if end >= nrows:
            end = nrows - 3
        workbookback.save(os.path.dirname(file_path) + '/平安人寿项目值守报告' + str(pp + 1) + '_' + t + '.xls')
        time.sleep(1)

def main():
    print('开始作业......')
    global j
    j = 2
    t1 = '平安人寿项目值守报告' + time.strftime('%m', time.localtime()) + '月' + time.strftime('%d', time.localtime()) + '日'
    if not os.path.exists(t1):
        os.mkdir(t1)
    csv_infos = read_csv()
    # print(csv_infos)
    scriptFile = csv_infos[0]['设备命令行文件名(需要带上文件后缀名)']
    print('总共有', len(csv_infos), '个职场')
    with open(scriptFile, 'rb') as f:
        group = ''
        for line in f:
            line = line.decode('utf8', 'ignore')
            if re.search('<--([\s\S]*?)-->', line):
                group = re.search('<--([\s\S]*?)-->', line).groups()[0]
                scriptLine[group] = []
            else:
                scriptLine[group].append(line.strip())
    # print(scriptLine)

    # 线程数
    poolNumber = len(csv_infos)

    t = time.strftime('%m%d_%H', time.localtime()) + '点' + time.strftime('%M', time.localtime())
    excelName = '平安人寿项目值守报告总表' + t + '.xls'
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet1')
    for i in range(0, 16):
        worksheet.col(i).width = 0x0d00 + 50 * 50
    # 第一行参数
    worksheet.write_merge(0, 1, 0, 0, '时间', style)
    worksheet.write_merge(0, 1, 1, 1, '设备名称', style)
    worksheet.write_merge(0, 1, 2, 2, 'IP', style)
    worksheet.write_merge(0, 1, 3, 3, '职场类别', style)
    worksheet.write_merge(0, 1, 4, 4, '职场人数', style)
    worksheet.write_merge(0, 1, 5, 5, '用户数(VLAN2)', style)
    worksheet.write_merge(0, 0, 6, 10, 'AR1', style)
    worksheet.write(1, 6, 'control', style)
    worksheet.write(1, 7, 'data', style)
    worksheet.write(1, 8, 'mem-usage', style)
    worksheet.write(1, 9, '上行', style)
    worksheet.write(1, 10, '下行', style)
    worksheet.write_merge(0, 0, 11, 15, 'AR2', style)
    worksheet.write(1, 11, 'control', style)
    worksheet.write(1, 12, 'data', style)
    worksheet.write(1, 13, 'mem-usage', style)
    worksheet.write(1, 14, '上行', style)
    worksheet.write(1, 15, '下行', style)
    poolUse(poolNumber, worksheet, csv_infos)
    tempp = '平安人寿项目值守报告' + time.strftime('%H', time.localtime()) + '点' + time.strftime('%M', time.localtime())

    if not os.path.exists(t1 + '/' + tempp):
        os.mkdir(t1 + '/' + tempp)

    workbook.save(t1 + '/' + tempp + '/' + excelName)
    time.sleep(3)
    split_table(t1 + '/' + tempp + '/' + excelName, t)

    # 发送邮件
    filename = os.path.dirname(os.path.abspath(__file__)) + '/' + t1 + '/' + tempp + '/' + excelName
    begin_send_email(filename)
    print('结束作业.......')

if __name__ == '__main__':
    main()

    # 做定时任务
    for shour in range(8, 11):
        for sminute in range(0, 60, 15):
            if sminute == 0:
                schedule.every().day.at(str(shour) + ':' + '00').do(main)
            else:
                if not (shour == 10 and sminute == 45):
                    schedule.every().day.at(str(shour) + ':' + str(sminute)).do(main)
    while True:
        schedule.run_pending()
        time.sleep(10)
        print('\r等待定时任务的启动中.........', end='')

logger.removeHandler(file_handler)
