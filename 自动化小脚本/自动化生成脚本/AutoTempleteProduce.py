import easygui
import pandas as pd
import wx
import os
import time
import re

sheet_config = '配置参数'
sheet_templete = '配置模板'
arr = []

class MyFrame(wx.Frame):
    '''界面'''
    def __init__(self, title):
        self.checkVarible = True
        self.collectVarible = 'Yes'
        self.filePathTemp = ''
        self.dirPathTemp = ''
        super(MyFrame, self).__init__(None, title=title, size=(563, 162))
        panel = wx.Panel(self)
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''确定按钮'''
        button3 = wx.Button(panel, -1, '确定', size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.OnButton3, button3)

        '''选择EXcel的地址选择框'''
        btnSizerStatic = wx.StaticText(panel, -1, 'excel表地址', style=wx.ALIGN_LEFT)
        self.filePath = wx.TextCtrl(panel, size=(200, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        btnSizerStatic.SetFont(font)
        button1 = wx.Button(panel, -1, '打开', size=(60, 30))
        button2 = wx.Button(panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.onButton1, button1)
        self.Bind(wx.EVT_BUTTON, self.OnButton2, button2)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(button1, proportion=0)
        btnSizer.Add(button2, proportion=0)

        '''配置模板的选择'''
        templeteStatic = wx.StaticText(panel, -1, '模板列的选择（A-Z）', style=wx.ALIGN_LEFT)
        templeteStatic.SetFont(font)
        self.templeteSelect = wx.TextCtrl(panel, size=(200, 30), style=wx.TE_MULTILINE)
        button4 = wx.Button(panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.onButton4, button4)

        '''配置生成文件夹的输入'''
        produceStatic = wx.StaticText(panel, -1, '配置存放目录', style=wx.ALIGN_LEFT)
        produceStatic.SetFont(font)
        self.produceStaticSelect = wx.TextCtrl(panel, size=(200, 30), style=wx.TE_MULTILINE)
        button5 = wx.Button(panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.onButton5, button5)

        # 排列
        wgui = wx.BoxSizer(wx.VERTICAL)
        wgui.Add(btnSizerStatic, flag = wx.ALIGN_CENTER)
        wgui.Add(templeteStatic, flag = wx.EXPAND)
        wgui.Add(produceStatic, flag=wx.ALIGN_CENTER)

        wgui1 = wx.BoxSizer(wx.VERTICAL)
        wgui1.Add(self.filePath, flag = wx.EXPAND)
        wgui1.Add(self.templeteSelect, flag = wx.EXPAND)
        wgui1.Add(self.produceStaticSelect, flag=wx.EXPAND)

        wgui2 = wx.BoxSizer(wx.VERTICAL)
        wgui2.Add(btnSizer, flag = wx.EXPAND)
        wgui2.Add(button4, flag = wx.EXPAND)
        wgui2.Add(button5, flag = wx.EXPAND)

        wgui3 = wx.BoxSizer()
        wgui3.Add(wgui, proportion=0, flag = wx.EXPAND)
        wgui3.Add(wgui1, proportion=0, flag = wx.EXPAND)
        wgui3.Add(wgui2, proportion=0, flag = wx.EXPAND)

        '''界面竖向排列下去'''
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(wgui3, proportion=-1, flag = wx.EXPAND)
        mainSizer1.Add(button3, proportion=-1, flag=wx.EXPAND)
        panel.SetSizer(mainSizer1)
        self.Center()
        self.Show()

    def onButton1(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.filePathTemp = fileDialog.GetPath()
        self.filePath.AppendText(self.filePathTemp)

    def OnButton2(self, event):
        self.filePath.Clear()

    def OnButton3(self, event):
        global arr
        arr = [self.filePathTemp, self.templeteSelect.GetValue(), self.produceStaticSelect.GetValue()]
        self.Close(True)

    def onButton4(self, event):
        self.templeteSelect.Clear()

    def onButton5(self, event):
        self.produceStaticSelect.Clear()

def config(filePath):
    '''
        :param filePath: 配置excel的路径
        :return: 配置参数
    '''
    configVariables = pd.read_excel(filePath, sheet_name = sheet_config).T
    index = configVariables.ix[0, :].tolist()
    index = [s.lower() for s in index]
    configVariables = configVariables.ix[:, :].T
    return index, configVariables

def templete(filePath, templeteRow):
    '''
        :param filePath: 配置excel的路径
        :return: 模板参数
    '''
    templeteVariabeles1 = pd.read_excel(filePath, sheet_name=sheet_templete, header=None)
    row = ord(templeteRow) - 65
    templeteVariabeles1 = templeteVariabeles1.ix[:, row]

    return templeteVariabeles1

def saveConfig(templete, templeteVariables, configVariables, savePath):
    '''
        :param templete:  模板
        :param templeteVariables:  模板的所有所需变量
        :param configVariables: 配置参数
        :param savePath: 保存配置路径
        :return: 将配置进行保存
    '''
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    # print(configVariables.shape[0])
    for i in range(configVariables.shape[0]):
        filePath = savePath + '\\' + str(configVariables.iloc[i, :].iloc[0]) + '.txt'
        f = open(filePath, 'w')
        for j in range(templete.shape[0]):
            line = templete.iloc[j]
            groups = re.findall('<.*?>', line)
            # print(groups)
            if groups:
                try:
                    for g in groups:
                        line = re.sub(g, str(configVariables.iloc[i, :][g.lower()]), line)
                    f.write(line + '\n')
                except Exception:
                    f.write(line + '\n')
            else:
                f.write(line + '\n')
        # f.close()

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame('自动化生成配置，初始参数')
    app.MainLoop()
    filePath, templeteRow, savePath = arr
    # filePath, templeteRow, savePath = [r'D:\shengkai\3.6\AutoTempleteProduce\配置基线.xlsx', 'A', 'sc']
    if filePath == '':
        filePath = '配置基线.xlsx'
    if templeteRow == '':
        templeteRow = 'A'
    if savePath == '':
        savePath = 'Scripts'
    templeteRow = templeteRow.upper()

    templeteVariables, configVariables = config(filePath)
    templete1 = templete(filePath, templeteRow)
    templete1 = templete1.dropna(axis=0, how='all')
    templete1.index = [x for x in range(templete1.shape[0])]
    configVariables.columns = [i.lower() for i in configVariables.columns.tolist()]
    try:
        saveConfig(templete1, templeteVariables, configVariables, savePath)
    except:
        pass
    time.sleep(2)
    easygui.msgbox('作业完成', title='提示框')




