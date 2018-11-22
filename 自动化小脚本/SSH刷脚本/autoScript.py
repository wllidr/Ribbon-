import paramiko
import time
import pandas as pd
import threadpool
import wx
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

class MyFrame(wx.Frame):
    def __init__(self,title):
        self.checkVarible = True
        self.collectVarible = 'Yes'
        self.filePathTemp = ''
        self.dirPathTemp = ''
        # super(MyFrame, self).__init__(None, title=title, size=(600,225))
        wx.Frame.__init__(self, None, -1, title, size=(600, 300))
        self.panel = wx.Panel(self)
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''选择EXcel的地址选择框'''
        btnSizerStatic = wx.StaticText(self.panel, -1, 'excel表地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.filePath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        btnSizerStatic.SetFont(font)
        button1 = wx.Button(self.panel, -1, '打开', size=(50, 30))
        button2 = wx.Button(self.panel, -1, '清除', size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.onButton1, button1)
        self.Bind(wx.EVT_BUTTON, self.OnButton2, button2)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(btnSizerStatic)
        btnSizer.Add(self.filePath)
        btnSizer.Add(button1, proportion=0)
        btnSizer.Add(button2, proportion=0)

        '''线程数'''
        btnSizerStatic = wx.StaticText(self.panel, -1, '线程数(填数字):', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.dirPath = wx.TextCtrl(self.panel, size=(350, 30), style=wx.TE_MULTILINE)
        btnSizerStatic.SetFont(font)
        button4 = wx.Button(self.panel, -1, '清除', size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton4, button4)
        dirSizer = wx.BoxSizer()
        dirSizer.Add(btnSizerStatic)
        dirSizer.Add(self.dirPath)
        dirSizer.Add(button4, proportion=0)

        '''是否刷脚本'''
        collectIf = wx.StaticText(self.panel, -1, '是否刷脚本：', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        collectIf.SetFont(font)
        radioCollect = wx.RadioButton(self.panel, -1, u'Yes', style=wx.RB_GROUP)
        radioCollect.SetForegroundColour("#0a74f7")
        radioCollect.SetFont(font)
        self.Bind(wx.EVT_RADIOBUTTON, self.radioColl, radioCollect)
        radioCollectNo = wx.RadioButton(self.panel, -1, u'No')
        radioCollectNo.SetForegroundColour("#f00")
        radioCollectNo.SetFont(font)
        self.Bind(wx.EVT_RADIOBUTTON, self.radioColl, radioCollectNo)
        radio = wx.BoxSizer()
        radio.Add(collectIf)
        radio.Add(radioCollect)
        radio.Add(radioCollectNo)

        '''是否使用SFTP'''
        checkIf = wx.StaticText(self.panel, -1, '刷脚本时是否需要进行验证: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        checkIf.SetFont(font)
        self.choice = ['Yes', 'No']
        chooseCheckChoice = wx.Choice(self.panel, -1, choices=self.choice, size=(60,30))
        chooseCheckChoice.SetFont(font)
        self.Bind(wx.EVT_CHOICE, self.radioCh, chooseCheckChoice)
        chooseCheckChoice.SetSelection(0)
        radioCheck = wx.BoxSizer()
        radioCheck.Add(checkIf)
        radioCheck.Add(chooseCheckChoice)
        # radioCheck.Add(radioCheckNo)

        '''脚本文件夹选择'''
        btnSizerStatic1 = wx.StaticText(self.panel, -1, '脚本文件夹地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.scriptPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        btnSizerStatic1.SetFont(font)
        button6 = wx.Button(self.panel, -1, '打开', size=(50, 30))
        button7 = wx.Button(self.panel, -1, '清除', size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton6, button6)
        self.Bind(wx.EVT_BUTTON, self.OnButton7, button7)
        dirSizer1 = wx.BoxSizer()
        dirSizer1.Add(btnSizerStatic1)
        dirSizer1.Add(self.scriptPath)
        dirSizer1.Add(button6, proportion=0)
        dirSizer1.Add(button7, proportion=0)

        '''确定按钮'''
        button5 = wx.Button(self.panel, -1, '确定', size=(50, 25))
        self.Bind(wx.EVT_BUTTON, self.OnButton5, button5)

        '''界面竖向排列下去'''
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(btnSizer, proportion=-1, flag = wx.ALIGN_RIGHT)
        mainSizer1.Add(dirSizer1, proportion=-1, flag = wx.ALIGN_RIGHT)
        mainSizer1.Add(dirSizer, proportion=-1, flag=wx.ALIGN_RIGHT)
        mainSizer1.Add(radio, proportion=-1, flag=wx.ALIGN_CENTER)
        mainSizer1.Add(radioCheck, proportion=-1, flag=wx.ALIGN_CENTER)
        mainSizer1.Add(button5, proportion=-1, flag=wx.ALIGN_CENTER)
        self.panel.SetSizer(mainSizer1)
        self.Center()
        self.Show()

    def onButton1(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN )
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.filePath.AppendText(fileDialog.GetPath())
        self.filePathTemp = fileDialog.GetPath()

    def OnButton2(self,event):
        self.filePath.Clear()

    def OnButton4(self, event):
        self.dirPath.Clear()

    def OnButton6(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.scriptPath.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton7(self, event):
        self.scriptPath.Clear()

    def radioCh(self, event):
        self.checkVarible  = event.GetEventObject().GetSelection()
        # print(self.checkVarible)
        if self.checkVarible == 1:
            self.checkVarible = False
        else:
            self.checkVarible = True

    def radioColl(self, event):
        self.collectVarible = event.GetEventObject().GetLabel()
        # print('self.collectVarible', self.collectVarible)

    def OnButton5(self, event):
        global arr
        if self.collectVarible == 'Yes':
            self.collectVarible = True
        else:
            self.collectVarible = False

        arr = [self.collectVarible, self.checkVarible, self.dirPath.GetValue(), self.filePathTemp, self.scriptPath.GetValue()]
        self.Close(True)

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
        # self.sftp_open()

    def ssh_connect(self):
        try:
            '''日志'''
            self.logger = logging.getLogger(self.host + '--' + self.device_name)
            formatter = logging.Formatter('%(message)s')
            self.fileHandler = logging.FileHandler(
                '.\\Logger\\' + t + '\\' + self.host + '--' + self.device_name + '.txt')
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
            # self.channel.settimeout(30)
            self.logger.info('Connect ' + self.device_name + ' device SSH Success...')
            self.channel.send('scr 0 t\n')
        except Exception as ex:
            self.logger.info('ssh %s@%s: %s' % (self.username, self.host, ex))

    def sftp_open(self):
        print(u'打开STTP成功')
        self.sftp_fd = self.ssh_fd.open_sftp()

    def sftp_put(self, from_path, to_path):
        '''上传文件到远程服务器'''
        return self.sftp_fd.put(from_path, to_path)

    def sftp_get(self, from_path, to_path):
        '''下载文件到本地'''
        return self.sftp_fd.get(from_path, to_path)

    def exe(self, cmd, checkIf):
        self.channel.send(cmd)
        time.sleep(0.5)
        info = ''
        if checkIf:
            while True:
                temp = self.channel.recv(65535)
                try:
                    info = info + temp.decode('utf8', 'ignore')
                except:
                    break
                info = re.sub('\\x1b\[\d*\w?', '', info)
                info = re.sub('\r\n', '\n', info)
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
    host = csv_info['设备IP']
    port = int(csv_info['设备端口号'])
    device_name = csv_info['设备名']
    username = csv_info['设备登录帐号']
    passwd = csv_info['设备登录密码']
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
            ssh = MySSH(host, port, username, passwd, script_file, device_name)
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

def main():
    app = wx.App()
    MyFrame('AutoSSH初始参数选择')
    app.MainLoop()
    scriptIf, checkIf, poolNumber, file_path, script_path = arr

    if poolNumber == '' or not poolNumber.isdigit():
        poolNumber = 20
    else:
        poolNumber = int(poolNumber)
    csv_infos = read_csv(file_path)

    if scriptIf:
        fun1 = partial(main_process, script_path)
        fun2 = partial(fun1, checkIf)
        pool = threadpool.ThreadPool(poolNumber)
        requests = threadpool.makeRequests(fun2, csv_infos)
        [pool.putRequest(req) for req in requests]
        pool.wait()

if __name__ == '__main__':
    if not os.path.exists('.\\Failed_log\\' + t):
        os.makedirs('.\\Failed_log\\' + t)
    if not os.path.exists('.\\Logger\\' + t):
        os.makedirs('.\\Logger\\' + t)
    temp = main()
    if temp:
        easygui.msgbox('异常退出！检查参数是否有误！！')
    else:
        easygui.msgbox('执行完成！请关闭！！')



