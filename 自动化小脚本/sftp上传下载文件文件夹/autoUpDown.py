import paramiko
import pandas as pd
import os
import re
import threadpool
import wx
import easygui
import logging
import sys
import hashlib

logger = logging.getLogger('Logger')
formatter = logging.Formatter('%(message)s')
fileHandler = logging.FileHandler('.\\上传下载.txt')
fileHandler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
# 终端日志按照指定的格式来写
console_handler.setFormatter(formatter)
# 可以设置日志的级别
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)
logger.addHandler(console_handler)

linux_root_list = []
src_root_list = []
linux_root = ''
src_root = r''
csv_path = r''
flag = True

class MyFrame(wx.Frame):
    def __init__(self,title):
        self.checkVarible = False
        self.flag = True
        # super(MyFrame, self).__init__(None, title=title, size=(600,225))
        wx.Frame.__init__(self, None, -1, title, size=(600, 220))
        self.panel = wx.Panel(self)
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''选择EXcel的地址选择框'''
        btnSizerStatic = wx.StaticText(self.panel, -1, 'excel表地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.filePath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        btnSizerStatic.SetFont(font)
        button1 = wx.Button(self.panel, -1, '打开', size=(60, 30))
        button2 = wx.Button(self.panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.selectFile, button1)
        self.Bind(wx.EVT_BUTTON, self.clear1, button2)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(btnSizerStatic, flag=wx.LEFT)
        btnSizer.Add(self.filePath, flag=wx.LEFT)
        btnSizer.Add(button1, flag=wx.LEFT)
        btnSizer.Add(button2, flag=wx.LEFT)

        '''windows路径'''
        windows = wx.StaticText(self.panel, -1, 'Windows端地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.windowsPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        windows.SetFont(font)
        button3 = wx.Button(self.panel, -1, '文件', size=(60, 30))
        button4 = wx.Button(self.panel, -1, '文件夹', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.selectFile1, button3)
        self.Bind(wx.EVT_BUTTON, self.selectDir, button4)
        btnSizer1 = wx.BoxSizer()
        btnSizer1.Add(windows, flag=wx.LEFT)
        btnSizer1.Add(self.windowsPath, flag=wx.LEFT)
        btnSizer1.Add(button3, flag=wx.LEFT)
        btnSizer1.Add(button4, flag=wx.LEFT)

        '''linux路径'''
        linux = wx.StaticText(self.panel, -1, 'Linux端地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.linuxPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        linux.SetFont(font)
        button6 = wx.Button(self.panel, -1, '清除', size=(120, 30))
        self.Bind(wx.EVT_BUTTON, self.clear2, button6)
        btnSizer2 = wx.BoxSizer()
        btnSizer2.Add(linux, flag=wx.LEFT)
        btnSizer2.Add(self.linuxPath, flag=wx.LEFT)
        btnSizer2.Add(button6, flag=wx.LEFT)

        '''上传还是下载'''
        downOrUp = wx.StaticText(self.panel, -1, '上传下载选择：', style= wx.CENTER)
        downOrUp.SetFont(font)
        self.choice = ['下载', '上传']
        chooseCheckChoice = wx.Choice(self.panel, -1, choices=self.choice, size=(100,30))
        chooseCheckChoice.SetFont(font)
        self.Bind(wx.EVT_CHOICE, self.downOrUpload, chooseCheckChoice)
        chooseCheckChoice.SetSelection(0)
        radio = wx.BoxSizer()
        radio.Add(downOrUp)
        radio.Add(chooseCheckChoice)

        '''确定按钮'''
        button5 = wx.Button(self.panel, -1, '确定', size=(50, 25))
        self.Bind(wx.EVT_BUTTON, self.OnButton5, button5)

        '''界面竖向排列下去'''
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(btnSizer, proportion=-1, flag = wx.ALIGN_RIGHT)
        mainSizer1.Add(btnSizer1, proportion=-1, flag=wx.ALIGN_RIGHT)
        mainSizer1.Add(btnSizer2, proportion=-1, flag=wx.ALIGN_RIGHT)
        mainSizer1.Add(radio, flag=wx.ALIGN_CENTER)
        mainSizer1.Add(button5, proportion=-1, flag=wx.ALIGN_CENTER)
        self.panel.SetSizer(mainSizer1)
        self.Center()
        self.Show()

    def selectFile(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN )
        fileDialog.ShowModal()
        self.filePath.AppendText(fileDialog.GetPath())

    def selectFile1(self, event):
        '''文件的选择'''
        self.windowsPath.Clear()
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN )
        fileDialog.ShowModal()
        self.windowsPath.AppendText(fileDialog.GetPath())

    def clear1(self, event):
        self.filePath.Clear()

    def clear2(self, event):
        self.linuxPath.Clear()

    def downOrUpload(self, event):
        if event.GetEventObject().GetSelection() == 1:
            self.flag = False
        else:
            self.flag = True

    def selectDir(self, event):
        self.windowsPath.Clear()
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.windowsPath.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton5(self, event):
        global arr
        # self.flag下载上传 , self.filePath CSV路径
        # self.windowsPath.GetValue(), self.linuxPath.GetValue() 上传下载路径
        arr = [self.flag, self.filePath.GetValue(), self.windowsPath.GetValue(), self.linuxPath.GetValue()]
        self.Close(True)

def read_csv(csvFile):
    df = pd.read_excel(csvFile, sheet_name='Sheet1', header=None)
    key = [i.strip() for i in df.ix[0, :].tolist()]
    csv_infos = []
    df = df.dropna(axis=0, how='all')
    df.index = [x for x in range(df.shape[0])]
    for i in range(1, df.shape[0]):
        temp = df.ix[i, :].tolist()
        temp1 = {}
        for i in range(len(temp)):
            temp1[str(key[i])] = str(temp[i])
        csv_infos.append(temp1)
    return csv_infos

def download(sftp, from_path, to_path, ssh_fd, retries = 5):
    logger.info('下载' + from_path + '到' + to_path + '中.....')
    stdin, stdout, stderr = ssh_fd.exec_command('md5sum ' + from_path + '\n')
    sftp.get(from_path, to_path)
    window_md5 = CalcMD5(to_path)
    for i, line in enumerate(stdout):
        line = line
    if window_md5 in line:
        logger.info('下载' + os.path.basename(from_path) + '完成.....')
    else:
        if retries > 0:
            logger.info('下载验证没有下载正确，重新下载' + from_path)
            download(sftp, from_path, to_path, ssh_fd, retries = retries - 1)
        else:
            logger.info('5次下载失败，请后面再重新尝试' + from_path)

def downloadPath(sftp, from_path):
    try:
        temps = sftp.listdir(from_path)
        for i in [from_path + '/' + temp for temp in temps]:
            stat = str(sftp.stat(i))
            if stat[0] == 'd':
                downloadPath(sftp, i)
                if not os.path.exists(src_root + re.sub(os.path.dirname(linux_root), '', i)):
                    os.makedirs(src_root + re.sub(os.path.dirname(linux_root), '', i))
            elif stat[0] == '-':
                src_root_list.append((src_root + re.sub(os.path.dirname(linux_root), '', i)).replace('\\', '/'))
                linux_root_list.append(i.replace('\\', '/'))
    except:
        src_root_list.append((src_root + re.sub(os.path.dirname(linux_root), '', from_path)).replace('\\', '/'))
        linux_root_list.append(from_path.replace('\\', '/'))

def put(sftp, from_path, to_path, ssh_fd, retries = 5):
    logger.info('上传' + from_path + '到' +  to_path + '中.....')
    sftp.put(from_path, to_path)
    stdin, stdout, stderr = ssh_fd.exec_command('md5sum ' + to_path + '\n')
    window_md5 = CalcMD5(from_path)
    for i, line in enumerate(stdout):
        line = line

    if window_md5 in line:
        logger.info('上传' + os.path.basename(from_path) + '完成.....')
    else:
        if retries > 0:
            logger.info('上传验证没有上传正确，重新上传....' + from_path)
            put(sftp, from_path, to_path, ssh_fd, retries = retries - 1)
        else:
            logger.info('5次上传失败，请后面再重新尝试' + from_path)

def putPath(sftp, from_path):
    if os.path.isdir(from_path):
        for i in os.listdir(from_path):
            putPath(sftp, os.path.join(from_path, i))
    else:
        src_root_list.append(from_path.replace('\\', '/'))
        path = re.sub(os.path.dirname(src_root), '', from_path)
        linux_root_list.append((linux_root + path).replace('\\', '/'))

def main_process(csv_info):
    host = csv_info['设备IP']
    port = int(csv_info['设备端口号'])
    device_name = csv_info['设备名']
    username = csv_info['设备登录帐号']
    password = csv_info['设备登录密码']
    logger.info(host + device_name + 'SSH连接中....')
    ssh_fd = paramiko.SSHClient()
    ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_fd.connect(host, port = port, username = username, password = password)

    sftp = paramiko.SFTPClient.from_transport(ssh_fd)
    logger.info(host + device_name + 'SFTP连接成功....')

    '''下载还是上传'''
    if flag:
        # 下载
        stat = str(sftp.stat(linux_root))
        if stat[0] == 'd':
            if not os.path.exists(src_root + re.sub(os.path.dirname(linux_root), '', linux_root)):
                os.mkdir(src_root + re.sub(os.path.dirname(linux_root), '', linux_root))
        # print(sftp.listdir(linux_root))
        downloadPath(sftp, linux_root)   # 下载路径组合成数组
        for i in range(len(linux_root_list)):
            download(sftp, linux_root_list[i], src_root_list[i], ssh_fd)
    else:
        # 上传
        putPath(sftp, src_root)
        if os.path.isdir(src_root):
            try:
                sftp.stat(os.path.join(linux_root, os.path.basename(src_root)).replace('\\', '/'))
            except:
                sftp.mkdir(os.path.join(linux_root, os.path.basename(src_root)).replace('\\', '/'))
        temp = [os.path.dirname(x) for x in linux_root_list]
        sorted(temp, key=len)
        for createDir in reversed(temp):
            try:
                sftp.stat(createDir.replace('\\', '/'))
            except:
                sftp.mkdir(createDir.replace('\\', '/'))
        for i in range(len(src_root_list)):
            put(sftp, src_root_list[i], linux_root_list[i], ssh_fd)
    sftp.close()
    ssh_fd.close()

def CalcMD5(filepath):
    '''MD5加密，用于校验保证完整性'''
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash

def main():
    csv_infos = read_csv(csv_path)
    pool = threadpool.ThreadPool(1)
    requests = threadpool.makeRequests(main_process, csv_infos)
    [pool.putRequest(req) for req in requests]
    pool.wait()

if __name__ == '__main__':
    app = wx.App()
    MyFrame('自动上传下载参数选择')
    app.MainLoop()
    flag, csv_path, src_root, linux_root = arr
    linux_root = linux_root.replace('\\', '/')
    src_root = src_root.replace('\\', '/')
    main()
    easygui.msgbox('传输完成！！！')

logger.removeFilter(console_handler)
logger.removeFilter(fileHandler)

