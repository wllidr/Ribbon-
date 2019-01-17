'''
    Author : Ribbon Huang
    Date : 2018 - 12 - 05
    Desc:
        ip 测试是否联通检测， 并且在联通后尝试 SSH 获取设备名....
'''
import subprocess
import threading
import time
import re
import threadpool
import xlwt
import pandas as pd
import os
import paramiko
from functools import partial
import easygui

# 设置居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
style = xlwt.XFStyle()  # Create the Pattern
style.alignment = alignment
workbook = xlwt.Workbook()
usedIp = []
unUsedIp = []

class MySSH:
    def __init__(self, host, port, username, passwd):
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.ssh_fd = None

    def ssh_connect(self):
        self.ssh_fd = paramiko.SSHClient()
        self.ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_fd.connect(self.host, port = self.port, username = self.username, password = self.password)
        self.channel = self.ssh_fd.invoke_shell()
        self.channel.timeout = 30
        self.channel.keep_this = self.ssh_fd

    def exe(self, cmd):
        '''有验证执行shell'''
        self.channel.send(cmd)
        time.sleep(0.5)
        info = ''
        while True:
            if cmd.strip() == self.password:
                break
            temp = self.channel.recv(65535)
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
        # print(info)
        return info

    def get_device_name(self):
        info = self.exe('display  current-configuration  |  include  sysname\n') + self.exe('#\n')
        deviceName = re.findall('sysname([\s\S]*?)\n', info)[-1].strip()
        return deviceName

    def close(self):
        '''SSH的关闭'''
        self.ssh_fd.close()


class PingThread(threading.Thread):  #
    def __init__(self, str_ip, sleep_time, port, username, password):
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.str_ip = str_ip
        self.port = port
        self.username = username
        self.password = password

    def run(self):
        global usedIp
        global unUsedIp
        time.sleep(self.sleep_time)
        ftp_sub = subprocess.Popen("ping %s -n 3" % self.str_ip, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        ret = ftp_sub.stdout.read()
        str_ret = ret.decode("gbk")
        ret_s = re.search("TTL", str_ret)
        if ret_s:
            ssh = MySSH(self.str_ip, self.port, self.username, self.password)
            try:
                ssh.ssh_connect()
                deviceName = ssh.get_device_name()
                usedIp.append({'ip': self.str_ip, 'device' : deviceName})
            except:
                usedIp.append({'ip': self.str_ip, 'device': '-----'})
            finally:
                ssh.close()
            # print(self.str_ip, 'OK')
        else:
            unUsedIp.append({'ip':self.str_ip, 'device' : '-----'})
            # print(self.str_ip, 'Failed')


def PingNetworkSegment(infos, port, username, password):
    global usedIp
    global unUsedIp
    global workbook

    worksheet = workbook.add_sheet('.'.join(infos[0]['ip'].split('.')[:-1]) + '网段信息')
    for i in range(0, 3):
        worksheet.col(i).width = 0x0d00 + 50 * 50
    # 第一行参数
    worksheet.write(0, 0, '设备名称', style)
    worksheet.write(0, 1, 'Ping得通Ip', style)
    worksheet.write(0, 2, 'Ping不通Ip', style)
    fun1 = partial(Ping, port)
    fun2 = partial(fun1, username)
    fun3 = partial(fun2, password)
    pool = threadpool.ThreadPool(300)
    requests = threadpool.makeRequests(fun3, infos)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    j = 1
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    usedIp = sorted(usedIp, key=lambda file: (int(file['ip'].split('--')[0].split('.')[-1]) + 1000 * int(file['ip'].split('--')[0].split('.')[-2])))
    unUsedIp = sorted(unUsedIp, key=lambda file: (int(file['ip'].split('--')[0].split('.')[-1]) + 1000 * int(file['ip'].split('--')[0].split('.')[-2])))
    # print(usedIp)
    # print(unUsedIp)
    for ip in usedIp:
        worksheet.write(j, 0, ip['device'], style)
        worksheet.write(j, 1, ip['ip'], style)
        worksheet.write(j, 2, '--', style)
        j += 1
    for ip in unUsedIp:
        worksheet.write(j, 0, ip['device'], style)
        worksheet.write(j, 1, '--', style)
        worksheet.write(j, 2, ip['ip'], style)
        j += 1
    usedIp = []
    unUsedIp = []

def Ping(port, username, password, info):
    PingThread(info['ip'], 3, port, username, password).run()

def main(file_path):
    infos = []
    df = pd.read_excel(file_path, sheet_name='IP检测器')
    df.dropna(axis=0, how='all')
    df = df.fillna(method='ffill', axis=0)
    start = df.iloc[0:, 0].tolist()
    end = df.iloc[0:, 1].tolist()
    # print(df)
    for i in range(df.shape[0]):
        username = df.loc[i:, '用户名'].tolist()[0]
        port = int(df.loc[i:, '端口号'].tolist()[0])
        password = df.loc[i:, '密码'].tolist()[0]
        # print(username, port, password)
        p1 = int(start[i].split('.')[-1])
        temp = '.'.join(start[i].split('.')[:-1])
        p2 = int(end[i].split('.')[-1])
        for p in range(p1, p2 + 1):
            infos.append({'ip': temp + '.' + str(p)})
        print('-----一个网段分割线------------------')
        print(infos[0]['ip'], '---->', infos[-1]['ip'], ' 所有Ip进行检测并且在成功后获取设备名称............')
        PingNetworkSegment(infos, port=port, username=username, password=password)
        infos = []


def begin_ip_scan(file_path):
    print('IP 扫描开始.........')
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    main(file_path)
    t = time.strftime('%Y%m%d_%H%M', time.localtime())
    workbook.save('自动生成文件文件夹' + '/' + 'ip扫描汇总表单' + t + '.xls')
    print('IP 扫描结束.........')
    easygui.msgbox('作业完成.....')

if __name__ == '__main__':
    file_path = r'D:\shengkai\3.6\集成应用\工具表格模板.xls'
    begin_ip_scan(file_path)