'''
    Desc:
        自动化刷脚本配置
'''
import paramiko
import time
import pandas as pd
import threadpool
from functools import partial
import logging
import sys
import os
import re
import easygui

src_root = ''
linux_root = ''
t = time.strftime('%Y%m%d_%H%M', time.localtime())
needMoreTimeSentence = ['save', 'commit', 'y', 'n']

class MySSH:
    def __init__(self, host, port, username, passwd, script_file, device_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.device_name = device_name
        self.ssh_fd = None
        self.sftp_fd = None
        self.script_file = script_file
        self.ssh_connect()

    def ssh_connect(self):
        try:
            '''日志'''
            self.logger = logging.getLogger(self.host + '--' + self.device_name)
            formatter = logging.Formatter('%(message)s')
            self.fileHandler = logging.FileHandler(
                '.\\Logger\\' + t + '\\' + self.host + '--' + self.device_name + '.txt', encoding='utf8')
            self.fileHandler.setFormatter(formatter)
            self.console_handler = logging.StreamHandler(sys.stdout)
            # 终端日志按照指定的格式来写
            self.console_handler.setFormatter(formatter)
            # 可以设置日志的级别
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(self.fileHandler)
            self.logger.addHandler(self.console_handler)

            self.logger.info('Connect ' + self.host + ' Device' + self.device_name + ' SSH ing.....')
            self.ssh_fd = paramiko.SSHClient()
            self.ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_fd.connect(self.host, port = self.port, username = self.username, password = self.password)
            self.channel = self.ssh_fd.invoke_shell()
            self.channel.keep_this = self.ssh_fd
            self.channel.settimeout(30)
            self.logger.info('Connect ' + self.device_name + ' device SSH Success...')
            self.channel.send('scr 0 t\n')
            self.channel.keep_this = self.ssh_fd
        except Exception as ex:
            self.logger.info('ssh %s@%s: %s' % (self.username, self.host, ex))

    def exe(self, cmd, checkIf):
        self.channel.send(cmd)
        time.sleep(0.5)
        info = ''
        if checkIf:
            while True:
                info = ''
                temp = self.channel.recv(65535)
                info = info + temp.decode('utf-8', 'ignore')
                info = re.sub('\\x1b\[\d*\w?', '', info)
                info = re.sub('\r\n', '\n', info)
                i = info.split('\n')
                temp = [p for p in i if p.strip() != '']
                info = '\n'.join(temp)
                self.logger.info(info)
                if cmd.strip().replace(' ', '') in info.replace(' ', ''):
                    break
                elif 'password' in info.lower() or re.search('\[\w.*?\]', info):
                    break
                else:
                    time.sleep(3)
        else:
            info = info + self.channel.recv(65535).decode('utf8', 'ignore')
            info = re.sub('\\x1b\[\d*\w?', '', info)
            info = re.sub('\r\n', '\n', info)
            self.logger.info(info)

        if re.search('\^', info) and re.search('Error', info) and re.search('Unrecognized', info) :
            with open('.\\Failed_log\\' + t + '\\' + self.host +'--' + self.device_name + '.txt', 'a') as f:
                f.write('Error statement: ' + cmd.strip() + '\n')
        return info

    def close(self):
        # self.sftp_fd.close()
        self.ssh_fd.close()
        self.logger.removeHandler(self.fileHandler)
        self.logger.removeHandler(self.console_handler)
        self.logger.info('close SSH success')

def read_csv(csvFile):
    df = pd.read_excel(csvFile, sheet_name='Sheet1', header=None)
    key = [i.strip() for i in df.iloc[0, :].tolist()]
    csv_infos = []
    df = df.dropna(axis=0, how='all')
    df.index = [x for x in range(df.shape[0])]
    for i in range(1, df.shape[0]):
        temp = df.iloc[i, :].tolist()
        temp1 = {}
        for i in range(len(temp)):
            temp1[str(key[i])] = str(temp[i])
        csv_infos.append(temp1)
    return csv_infos

def main_process(script_path, checkIf, csv_info, retry = 3):
    host = csv_info['设备IP'].strip()
    port = int(csv_info['设备端口号'].strip())
    device_name = csv_info['设备名'].strip()
    username = csv_info['设备登录帐号'].strip()
    passwd = csv_info['设备登录密码'].strip()
    if script_path == '':
        script_path = 'scripts'
    script_file = script_path + '\\' + csv_info['设备命令行文件名(需要带上文件后缀名)']

    try:
        f = open(script_file, 'r')
    except:
        with open('.\\Failed_log\\' + t + '\\' + host + '--' + device_name + '.txt', 'a') as f:
            f.write('读取脚本失败，请查询路径是否有问题!! \n')
        return None

    flag = ''
    if retry > 0:
        try:
            ssh = MySSH(host.strip(), port, username, passwd, script_file, device_name)
            for cmd in f:
                ssh.exe(cmd, checkIf)
            ssh.exe('#\n', checkIf)
        except Exception as e:
            flag = str(e)
            if retry == 1:
                with open('.\\Failed_log\\' + t + '\\' + host + '--' + device_name + '.txt', 'a') as f:
                    f.write('三次SSH失败， 请检查网络是否有问题！！\n')
        finally:
            f.close()
            ssh.close()
            if flag != '':
                if retry != 1:
                    with open('.\\Logger\\' + t + '\\'+ host + '--' + device_name + '.txt', 'a') as f:
                        f.write('The ' + str(4 - retry) + ' times SSH retried connect.....\n')
                    time.sleep(10)
                    main_process(script_path, checkIf, csv_info, retry = retry - 1)

def main(checkIf, poolNumber, file_path, script_path):
    if poolNumber == '' or not poolNumber.isdigit():
        poolNumber = 20
    else:
        poolNumber = int(poolNumber)
    csv_infos = read_csv(file_path)

    fun1 = partial(main_process, script_path)
    fun2 = partial(fun1, checkIf)
    pool = threadpool.ThreadPool(poolNumber)
    requests = threadpool.makeRequests(fun2, csv_infos)
    [pool.putRequest(req) for req in requests]
    pool.wait()

def autoScriptBegin(checkIf, poolNumber, file_path, script_path):
    if not os.path.exists('.\\Failed_log\\' + t):
        os.makedirs('.\\Failed_log\\' + t)
    if not os.path.exists('.\\Logger\\' + t):
        os.makedirs('.\\Logger\\' + t)
    print('开始刷脚本...............')
    temp = main(checkIf, poolNumber, file_path, script_path)
    print('刷脚本结束...............')
    if temp:
        easygui.msgbox('异常退出！检查参数是否有误！！')
    else:
        easygui.msgbox('执行完成！可关闭程序，或者重新选择所需功能！！')