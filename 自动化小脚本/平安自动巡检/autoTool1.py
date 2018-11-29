'''
    Date : 2018 - 11 - 27
    Author :Ribbon Huang
    Desc:
        平安自动巡检报告自动生成。自动微信发送，自动截图excel
'''
import pandas as pd
import time
import paramiko
import re
import threadpool
import xlwt
from functools import partial
import datetime
from win32com.client import DispatchEx
import pythoncom
from PIL import ImageGrab
import uuid
import os
import itchat

itchat.auto_login(hotReload=True)   #热启动你的微信
rooms=itchat.get_chatrooms(update=True)

j = 2
excelline = 1
scriptLine = {}
t = time.strftime('%m%d', time.localtime())
# 设置居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('Sheet1')
style = xlwt.XFStyle()  # Create the Pattern
style.alignment = alignment
for i in range(0, 7):
    worksheet.col(i).width = 0x0d00 + 50*50

class MySSH:
    def __init__(self, host, port, username, passwd, device_name, worksheet):
        self.worksheet = worksheet
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.device_name = device_name
        self.ssh_fd = None
        self.ssh_connect()

    def ssh_connect(self):
        self.ssh_fd = paramiko.SSHClient()
        self.ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_fd.connect(self.host, port = self.port, username = self.username, password = self.password)
        self.channel = self.ssh_fd.invoke_shell()
        self.channel.settimeout(150)
        self.channel.send('scr 0 t\n')

    def exe(self, cmd):
        # 有验证执行shell
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
        print(info)
        return info

    def stelnet133(self, ip, username, password):
        self.exe('sys' + '\n')
        info = self.exe('stelnet ' + ip + ' 55522' + '\n')
        if re.search('inputtheusername', re.sub(' ', '', info)):
            info = self.exe(username + '\n')
            time.sleep(5)
        else:
            time.sleep(10)
            self.exe(username + '\n')
        while True:
            if re.search('Continuetoaccessit?[Y/N]', re.sub(' ', '', info)):
                info = self.exe('y' + '\n')
            elif re.search('publickey?[Y/N]', re.sub(' ', '', info)):
                info = self.exe('n' + '\n')
            elif re.search('Enterpassword', re.sub(' ', '', info)):
                info = self.exe(password + '\n')
                break
            else:
                time.sleep(10)
                info = self.exe('y' + '\n')

    def get_used(self):
        '''表格写入获取的参数'''
        global j
        global style
        # 得到CPU、内存使用率
        cpu = self.cpuUse()
        memory = self.memoryUse()

        # 年月日时分
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().month)
        day = str(datetime.datetime.now().day)
        hour = str(datetime.datetime.now().hour)
        minute = str(datetime.datetime.now().minute)

        # used的获取， 以及所有获取参数表格写入
        info1 = self.exe('dis ip interface brief ' + '\n')
        info2 = self.exe('#' + '\n')
        info = info1.lower() + info2.lower()
        if re.search('vlanif2', info):
            # 有vlanif2 则可以直接获取used
            for line in scriptLine['获取used']:
                info = self.exe(line + '\n')
                info += self.exe('#\n')
                if re.search('notexist', re.sub(' ', '', info)):
                    continue
                else:
                    start = info.index('Used')
                    info = info[start: ]
                    # print(info)
                    used = [a for a in re.search('(133\.\d*?\.\d*?\.[\s\S]*?)\n', info).groups()[0].split(' ') if a!='']
                    self.worksheet.write(j, 0, year + '年' + month + '月' + day + '日' + hour + '时' + minute + '分', style)
                    self.worksheet.write(j, 1, self.device_name, style)
                    self.worksheet.write(j, 2, self.host, style)
                    self.worksheet.write(j, 3, used[-4], style)
                    self.worksheet.write(j, 4, cpu[0].strip(), style)
                    self.worksheet.write(j, 5, cpu[1].strip(), style)
                    self.worksheet.write(j, 6, memory.strip(), style)
                    j += 1
                    break
        else:
            temp = re.search('(133.[\s\S]*?)/', info).groups()[0]
            temp = temp.split('.')
            ip = '.'.join(temp[0: -1]) + '.' + str(int(temp[-1]) - 1)
            self.stelnet133(ip, self.username, self.password)
            for line in scriptLine['获取used']:
                info = self.exe(line + '\n')
                info += self.exe('#\n')
                if re.search('notexist', re.sub(' ', '', info)):
                    # print('not exist')
                    continue
                else:
                    info += self.exe('#\n')
                    start = info.index('Used')
                    info = info[start: ]
                    print(info)
                    used = [a for a in re.search('(133\.\d*?\.\d*?\.[\s\S]*?)\n', info).groups()[0].split(' ') if a != '']
                    # print(used)
                    self.worksheet.write(j, 0, year + '年' + month + '月' + day + '日' + hour + '时' + minute + '分', style)
                    self.worksheet.write(j, 1, self.device_name, style)
                    self.worksheet.write(j, 2, self.host, style)
                    self.worksheet.write(j, 3, used[-4], style)
                    self.worksheet.write(j, 4, cpu[0].strip(), style)
                    self.worksheet.write(j, 5, cpu[1].strip(), style)
                    self.worksheet.write(j, 6, memory.strip(), style)
                    j += 1
                    return None

    def cpuUse(self):
        for line in scriptLine['获取CPU利用率']:
            info = self.exe(line + '\n')
            info += self.exe('#' + '\n')
            cpu = re.findall('CPU Usage: ([\s\S]*?)Max', info)
        # print(cpu)
        return cpu

    def memoryUse(self):
        for line in scriptLine['获取内存利用率']:
            info = self.exe(line + '\n')
            info += self.exe('#' + '\n')
            memory = re.search('Memory Using Percentage Is:([\s\S]*?)\n', info).groups()[0]
        # print(memory)
        return memory

    def close(self):
        self.ssh_fd.close()

def read_csv():
    file = r'路由器参数.xls'
    df = pd.read_excel(file, header=None)
    df = df.fillna(method='ffill', axis=0)
    # print(df)
    df = df.drop_duplicates(1, 'first')
    key = [str(i).strip() for i in df.iloc[0, :].tolist()]
    # print(key)
    csv_infos = []
    df.index = [x for x in range(df.shape[0])]
    for i in range(1, df.shape[0]):
        temp = df.iloc[i, :].tolist()
        temp1 = {}
        for i in range(len(temp)):
            temp1[str(key[i])] = str(temp[i])
        csv_infos.append(temp1)
    return csv_infos

def main_process(worksheet, csv_info, retried = 5):
    device_name = csv_info['设备名']
    host = csv_info['设备IP']
    port = csv_info['设备端口号']
    username = csv_info['设备登录帐号']
    password = csv_info['设备登录密码']
    ssh = MySSH(host=host, port=port, username=username, passwd=password, device_name=device_name, worksheet=worksheet)
    try:
        ssh.ssh_connect()
        ssh.get_used()
    except:
        if retried > 0:
            time.sleep(10)
            main_process(worksheet, csv_info, retried=retried-1)
    finally:
        ssh.close()

def poolUse(poolNumber, worksheet, csv_infos):
    fun1 = partial(main_process, worksheet)
    pool = threadpool.ThreadPool(poolNumber)
    requests = threadpool.makeRequests(fun1, csv_infos)
    [pool.putRequest(req) for req in requests]
    pool.wait()

def excel_catch_screen(filename, sheetname, screen_area, img_name=False):
    '''excel截图'''
    filename = os.path.join(os.path.dirname(__file__), filename)
    pythoncom.CoInitialize()  # excel多线程相关
    excel = DispatchEx("Excel.Application")  # 启动excel
    excel.Visible = True  # 可视化
    excel.DisplayAlerts = False  # 是否显示警告
    wb = excel.Workbooks.Open(filename)  # 打开excel
    ws = wb.Sheets(sheetname)  # 选择sheet
    ws.Range(screen_area).CopyPicture()  # 复制图片区域
    ws.Paste()  # 粘贴 ws.Paste(ws.Range('B1'))  # 将图片移动到具体位置
    name = str(uuid.uuid4())  # 重命名唯一值
    new_shape_name = name[:6]
    excel.Selection.ShapeRange.Name = new_shape_name  # 将刚刚选择的Shape重命名，避免与已有图片混淆
    ws.Shapes(new_shape_name).Copy()  # 选择图片
    img = ImageGrab.grabclipboard()  # 获取剪贴板的图片数据
    img_name = "screenshot.png"
    img.save(img_name)  # 保存图片
    wb.Close(SaveChanges=0)  # 关闭工作薄，不保存
    excel.Quit()  # 退出excel
    pythoncom.CoUninitialize()

if __name__ == '__main__':
    csv_infos = read_csv()
    # print(csv_infos)
    scriptFile = csv_infos[0]['设备命令行文件名(需要带上文件后缀名)']
    roomName = csv_infos[0]['群名']
    print('总共有', len(csv_infos), '台设置需要完成自动化配置获取')
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
    if len(csv_infos) > 100 :
        poolNumber = 100
    else:
        poolNumber = len(csv_infos)

    # 第一行参数
    worksheet.write_merge(0,1, 0 ,0 , '时间', style)
    worksheet.write_merge(0, 1, 1, 1, '设备名称', style)
    worksheet.write_merge(0, 1, 2, 2, 'IP', style)
    worksheet.write_merge(0, 1, 3, 3, '用户数(VLAN2)', style)
    worksheet.write_merge(0, 0, 4, 5, 'CPU-USAGE', style)
    worksheet.write(1, 4, 'control', style)
    worksheet.write(1, 5, 'data', style)
    worksheet.write_merge(0, 1, 6, 6, 'MEMORY-USAGE', style)

    while True:
        poolUse(poolNumber, worksheet, csv_infos)
        if t != time.strftime('%m%d', time.localtime()):
            t = time.strftime('%m%d', time.localtime())
            j = 2
            i = 1
            worksheet.write_merge(0, 1, 0, 0, '时间', style)
            worksheet.write_merge(0, 1, 1, 1, '设备名称', style)
            worksheet.write_merge(0, 1, 2, 2, 'IP', style)
            worksheet.write_merge(0, 1, 3, 3, '用户数(VLAN2)', style)
            worksheet.write_merge(0, 0, 4, 5, 'CPU-USAGE', style)
            worksheet.write(1, 4, 'control', style)
            worksheet.write(1, 5, 'data', style)
            worksheet.write_merge(0, 1, 6, 6, 'MEMORY-USAGE', style)

        excelName = '平安人寿项目值守报告' + t + '.xls'
        workbook.save(excelName)
        time.sleep(5)
        print('结束一次')
        try:
            shape = "A" + str(excelline) + ':G' + str(pd.read_excel(excelName, header=None).shape[0])
            excelline = pd.read_excel(excelName, header=None).shape[0] + 3
            # print(shape)
            excel_catch_screen(excelName, "Sheet1", shape)
            time.sleep(3)
            try:

                roomUser = ''
                for i in range(len(rooms)):
                    if rooms[i]['NickName'] == roomName:
                        roomUser = rooms[i]['UserName']
                itchat.send_image("screenshot.png", toUserName=roomUser)
            except:
                roomUser = ''
                itchat.auto_login(hotReload=True)  # 热启动你的微信
        except:
            pass
        finally:
            j += 3
        time.sleep(600)
        print('新的开始')