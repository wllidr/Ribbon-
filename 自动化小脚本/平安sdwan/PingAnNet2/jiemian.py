import sys; sys.path.append('.')
import wx
import wx.grid
import tableVariables
import configFiles
import dealFwFile
import dealSwFile
import dealAcFile
import easygui

wildcardMark = {'1': '127.255.255.255', '2': '63.255.255.255', '3': '31.255.255.255', '4': '15.255.255.255',
                '5': '7.255.255.255', '6': '3.255.255.255', '7': '1.255.255.255', '8': '0.255.255.255',
                '9': '0.127.255.255', '10': '0.63.255.255', '11': '0.31.255.255', '12': '0.15.255.255',
                '13': '0.7.255.255', '14': '0.3.255.255', '15': '0.1.255.255', '16': '0.0.255.255',
                '17': '0.0.127.255', '18': '0.0.63.255', '19': '0.0.31.255', '20': '0.0.15.255',
                '21': '0.0.7.255', '22': '0.0.3.255', '23': '0.0.1.255', '24': '0.0.0.255',
                '25': '0.0.0.127', '26': '0.0.0.63', '27': '0.0.0.31', '28': '0.0.0.15', '29': '0.0.0.7',
                '30': '0.0.0.3', '31': '0.0.0.1', '32': '0.0.0.0'}

class MyFrame(wx.Frame):
    def __init__(self, title):
        self.page = [1, 2, 3, 4, 5, 6]
        self.acprev = ''
        self.i = 0
        self.ipPlans, self.bussniessClass, self.devices, self.swModel, self.fwYN = tableVariables.InitialVariables()
        self.acFiles, self.swFile, self.fwFile = configFiles.fileSelect(self.bussniessClass, self.fwYN, self.devices, self.swModel, self.ipPlans)
        self.dns1 = self.dns2 = self.option = self.optionSelect = ''
        self.swPortConnect = []
        self.fwPortConnect = []
        for i in range(len(self.acFiles)):
            self.swPortConnect.append({'0':'', '1':'', '2':'', '3':'', 'mad':''})
            self.fwPortConnect.append({'0':'', '1':'', '2':'', '3':'', 'mad':''})
        self.updownConnect = ['']
        self.updownConnectAc = []
        self.acPortConnects = None
        self.ac1textvalue = self.ac2textvalue = self.optiontextvalue = ''
        wx.Frame.__init__(self, None, -1, title, size=(700, 600))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        '''职场类别'''
        busniessClassStatic = wx.StaticText(self.panel, -1, '职场类别: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        busniessClassStatic.SetFont(font)
        busniessClassChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        busniessClassChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        busniessClassChoice.SetValue(self.bussniessClass.upper())
        swModelStatic = wx.StaticText(self.panel, -1, '   核心型号: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        swModelStatic.SetFont(font)
        swModelChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        swModelChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        swModelChoice.SetValue(self.swModel)
        fwModelStatic = wx.StaticText(self.panel, -1, '   有无防火墙: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        fwModelStatic.SetFont(font)
        fwYNChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        fwYNChoice.SetValue(self.fwYN)
        fwYNChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        radioCheck = wx.BoxSizer()
        radioCheck.Add(busniessClassStatic)
        radioCheck.Add(busniessClassChoice)
        radioCheck.Add(swModelStatic)
        radioCheck.Add(swModelChoice)
        radioCheck.Add(fwModelStatic)
        radioCheck.Add(fwYNChoice)

        '''起始页表格'''
        grid = wx.grid.Grid(self.panel, -1)
        grid.CreateGrid(len(self.devices), 5)
        grid.SetGridCursor((4, 4))
        grid.SetColLabelValue(0, '设备名称')
        grid.SetColLabelValue(1, '设备角色')
        grid.SetColLabelValue(2, '设备类型')
        grid.SetColLabelValue(3, '堆叠台数')
        grid.SetColLabelValue(4, '上联设备')
        grid.SetRowLabelSize(1)
        # for i in range(0, 5):
        grid.SetColSize(0, 250)
        grid.SetColSize(1, 150)
        grid.SetColSize(2, 200)
        grid.SetColSize(4, 250)

        for i in range(len(self.devices)):
            grid.SetRowSize(i, 26)
            j = 0
            for key,value in self.devices[i].items():
                grid.SetCellValue(i, j, str(value))
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                j += 1
        grid.SetReadOnly(0,0)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
            swModelChoice.Disable()
        else:
            swModelChoice.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER| wx.ALL, border=5)
        mainSizer1.Add(radioCheck, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(grid, proportion=0, flag=wx.ALIGN_CENTER| wx.ALL, border=5)
        self.panel.SetSizer(mainSizer1)

        mainSizer1.SetMinSize((1100, 600))
        mainSizer1.Fit(self)
        self.Center()

    def firstPage(self, event):
        self.i += 1
        if self.i > 5:
            self.i = 0
        self.panel.Destroy()
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        '''职场类别'''
        busniessClassStatic = wx.StaticText(self.panel, -1, '职场类别: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        busniessClassStatic.SetFont(font)
        busniessClassChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        busniessClassChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        busniessClassChoice.SetValue(self.bussniessClass.upper())
        swModelStatic = wx.StaticText(self.panel, -1, '   核心型号: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        swModelStatic.SetFont(font)
        swModelChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        swModelChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        swModelChoice.SetValue(self.swModel)
        fwModelStatic = wx.StaticText(self.panel, -1, '   有无防火墙: ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        fwModelStatic.SetFont(font)
        fwYNChoice = wx.TextCtrl(self.panel, size=(120, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        fwYNChoice.SetValue(self.fwYN)
        fwYNChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        radioCheck = wx.BoxSizer()
        radioCheck.Add(busniessClassStatic)
        radioCheck.Add(busniessClassChoice)
        radioCheck.Add(swModelStatic)
        radioCheck.Add(swModelChoice)
        radioCheck.Add(fwModelStatic)
        radioCheck.Add(fwYNChoice)

        '''起始页表格'''
        grid = wx.grid.Grid(self.panel, -1)
        grid.CreateGrid(len(self.devices), 5)
        grid.SetGridCursor((4, 4))
        grid.SetColLabelValue(0, '设备名称')
        grid.SetColLabelValue(1, '设备角色')
        grid.SetColLabelValue(2, '设备类型')
        grid.SetColLabelValue(3, '堆叠台数')
        grid.SetColLabelValue(4, '上联设备')
        grid.SetRowLabelSize(1)
        # for i in range(0, 5):
        grid.SetColSize(0, 250)
        grid.SetColSize(1, 150)
        grid.SetColSize(2, 200)
        grid.SetColSize(4, 250)

        for i in range(len(self.devices)):
            grid.SetRowSize(i, 26)
            j = 0
            for key, value in self.devices[i].items():
                grid.SetCellValue(i, j, str(value))
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                j += 1
        grid.SetReadOnly(0, 0)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
            swModelChoice.Disable()
        else:
            swModelChoice.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(radioCheck, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(grid, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel.SetSizer(mainSizer1)

        mainSizer1.SetMinSize((1100 + self.page[self.i], 600))
        mainSizer1.Fit(self)

    def SWUI(self, event):
        self.i += 1
        if self.i > 5:
            self.i = 0
        self.panel.Destroy()

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        # 核心sysname
        sysNameStatic = wx.StaticText(self.panel, -1, '设备名称:    ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        swSysname = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        swSysname.SetValue(self.swFile['sysname'])
        sysNameStatic.SetFont(font)
        box1 = wx.BoxSizer()
        box1.Add(sysNameStatic)
        box1.Add(swSysname)

        # DNS1, 2
        dns1Static = wx.StaticText(self.panel, -1, 'DNS1:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        dns2Static = wx.StaticText(self.panel, -1, '   DNS2:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.dns1Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
        self.dns2Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
        self.dns1Text.AppendText(self.dns1)
        self.dns2Text.AppendText(self.dns2)
        dns1Static.SetFont(font)
        dns2Static.SetFont(font)
        box2 = wx.BoxSizer()
        box2.Add(dns1Static)
        box2.Add(self.dns1Text)
        box2.Add(dns2Static)
        box2.Add(self.dns2Text)

        # option
        optionStatic = wx.StaticText(self.panel, -1, 'Option:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        optionStatic.SetFont(font)
        self.options = ['', '43', '148', '43 & 148']
        option = wx.Choice(self.panel, -1, choices=self.options , size=(100, 30), style=wx.LB_MULTIPLE)
        option.SetSelection(0)
        option.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        AC1Static = wx.StaticText(self.panel, -1, '   AC1:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        AC1Static.SetFont(font)
        self.swAC1Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
        self.Bind(wx.EVT_CHOICE, self.optionChoice, option)
        AC1Static2 = wx.StaticText(self.panel, -1, '   AC2:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        AC1Static2.SetFont(font)
        self.swAC2Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
        # print(self.options.index(self.optionSelect))
        option.SetSelection(self.options.index(self.optiontextvalue))
        self.swAC1Text.SetValue(self.ac1textvalue)
        self.swAC2Text.SetValue(self.ac2textvalue)
        box3 = wx.BoxSizer()
        box3.Add(optionStatic)
        box3.Add(option)
        box3.Add(AC1Static)
        box3.Add(self.swAC1Text)
        box3.Add(AC1Static2)
        box3.Add(self.swAC2Text)
        if self.optionSelect == '':
            self.swAC1Text.Disable()
            self.swAC2Text.Disable()
        else:
            self.swAC1Text.Enable()
            self.swAC2Text.Enable()

        # 接口连接表格
        self.grid = wx.grid.Grid(self.panel, -1)
        self.grid.CreateGrid(len(self.acFiles), 4)
        self.grid.SetGridCursor((4, 4))
        self.grid.SetColLabelValue(0, '接口1')
        self.grid.SetColLabelValue(1, '接口2')
        self.grid.SetColLabelValue(2, 'Eth-Trunk')
        self.grid.SetColLabelValue(3, 'Mad')
        for i in range(0, 4):
            self.grid.SetColSize(i, 250)
        for i in range(0, len(self.acFiles)):
            self.grid.SetRowSize(i, 25)
        for i in range(0,len(self.acFiles)):
            self.grid.SetCellValue(i, 0, self.swPortConnect[i]['0'])
            self.grid.SetCellValue(i, 1, self.swPortConnect[i]['1'])
            self.grid.SetCellValue(i, 2, self.swPortConnect[i]['2'])
            self.grid.SetCellValue(i, 3, self.swPortConnect[i]['mad'])
        portChoice1 =  [''] + ['GigabitEthernet1/0/' + str(i) for i in range(24, 0, -1)]
        portChoice2 = [''] + ['GigabitEthernet2/0/' + str(i) for i in range(24, 0, -1)]
        portChoice3 = [''] + ['Eth-Trunk' + str(i) for i in range(1, 20)]
        portChoice4 = ['', 'mad']
        for i in range(len(self.acFiles)):
            self.grid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice1))
            self.grid.SetCellAlignment(i, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(len(self.acFiles)):
            self.grid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice2))
            self.grid.SetCellAlignment(i, 1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(len(self.acFiles)):
            self.grid.SetCellEditor(i, 2, wx.grid.GridCellChoiceEditor(choices=portChoice3))
            self.grid.SetCellAlignment(i, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(len(self.acFiles)):
            self.grid.SetCellEditor(i, 3, wx.grid.GridCellChoiceEditor(choices=portChoice4))
            self.grid.SetCellAlignment(i, 3, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self.grid.SetRowLabelSize(30)
        self.grid.SetRowLabelSize(1)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
        else:
            button2.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()

        '''确定按钮'''
        sure = wx.Button(self.panel, -1, '接口关系确认按钮', size=(200, 30))
        sure.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.OnSureSwPorts, sure)

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(box1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(box3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(box2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(self.grid, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(sure, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel.SetSizer(mainSizer1)

        mainSizer1.SetMinSize((1100 + self.page[self.i], 600))
        mainSizer1.Fit(self)

    def optionChoice(self, event):
        self.optionSelect = self.options[int(event.GetEventObject().GetSelection())]
        if self.optionSelect == '':
            self.swAC1Text.Disable()
            self.swAC2Text.Disable()
            self.swAC2Text.SetValue('')
            self.swAC1Text.SetValue('')
        else:
            self.swAC1Text.Enable()
            self.swAC2Text.Enable()

    def OnSureSwPorts(self, event):
        self.dns1 = self.dns1Text.GetValue()
        self.dns2 = self.dns2Text.GetValue()
        self.ac1textvalue = self.swAC1Text.GetValue()
        self.ac2textvalue = self.swAC2Text.GetValue()
        self.optiontextvalue = self.optionSelect
        if self.optionSelect == '':
            self.option = ''
        elif self.optionSelect == '43':
            self.option = 'dhcp server option 43 sub-option 2 ip-address ' + self.swAC1Text.GetValue() + ' ' +self.swAC2Text.GetValue()
        elif self.optionSelect == '148':
            self.option = 'dhcp server option 148 ascii agilemode=agile-cloud;agilemanage-mode=domain;agilemanage-domain=device-naas1.huawei.com;agilemanage-port=10020;'
        else:
            self.option = 'dhcp server option 43 sub-option 2 ip-address ' + self.swAC1Text.GetValue() + ' ' + self.swAC2Text.GetValue() + '\n'
            self.option = ' dhcp server option 148 ascii agilemode=agile-cloud;agilemanage-mode=domain;agilemanage-domain=device-naas1.huawei.com;agilemanage-port=10020;'
        for i in range(len(self.acFiles)):
            self.swPortConnect[i]['0'] = self.grid.GetCellValue(i, 0)
            self.swPortConnect[i]['1'] = self.grid.GetCellValue(i, 1)
            self.swPortConnect[i]['2'] = self.grid.GetCellValue(i, 2)
            self.swPortConnect[i]['mad'] = self.grid.GetCellValue(i, 3)
        for port in self.swPortConnect:
            if port['0'] != '' and port['1'] != '' and port['2'] != '':
                self.updownConnect.append(port['2'])
            elif port['0'] != '' and port['1'] == '' and port['2'] == '':
                self.updownConnect.append(port['0'])
            elif port['0'] == '' and port['1'] != '' and port['2'] == '':
                self.updownConnect.append(port['1'])
        self.updownConnect = list(set(self.updownConnect))

    def FWUI(self, event):
        self.i += 1
        if self.i > 5:
            self.i = 0
        self.panel.Destroy()

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        # 防火墙
        sysNameStatic = wx.StaticText(self.panel, -1, '设备名称:    ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        fwSysname = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        fwSysname.AppendText(self.fwFile['sysname'])
        sysNameStatic.SetFont(font)
        box1 = wx.BoxSizer()
        box1.Add(sysNameStatic)
        box1.Add(fwSysname)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
        else:
            button2.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(box1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        if 'D' in self.bussniessClass or 'E' in self.bussniessClass:
            # 接口连接表格
            self.fwgrid = wx.grid.Grid(self.panel, -1)
            self.fwgrid.CreateGrid(len(self.acFiles), 4)
            self.fwgrid.SetGridCursor((4, 4))
            self.fwgrid.SetColLabelValue(0, '接口1')
            self.fwgrid.SetColLabelValue(1, '接口2')
            self.fwgrid.SetColLabelValue(2, 'Eth-Trunk')
            self.fwgrid.SetColLabelValue(3, 'Mad')
            for i in range(0, 4):
                self.fwgrid.SetColSize(i, 250)
            for i in range(0, len(self.acFiles)):
                self.fwgrid.SetRowSize(i, 25)
            for i in range(0, len(self.acFiles)):
                self.fwgrid.SetCellValue(i, 0, self.fwPortConnect[i]['0'])
                self.fwgrid.SetCellValue(i, 1, self.fwPortConnect[i]['1'])
                self.fwgrid.SetCellValue(i, 2, self.fwPortConnect[i]['2'])
                self.fwgrid.SetCellValue(i, 3, self.fwPortConnect[i]['mad'])
            portChoice1 = [''] + ['GigabitEthernet0/0/' + str(i) for i in range(3, 8)]
            portChoice3 = [''] + ['Eth-Trunk' + str(i) for i in range(1, 4)]
            portChoice4 = ['', 'mad']
            for i in range(len(self.acFiles)):
                self.fwgrid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice1))
                self.fwgrid.SetCellAlignment(i, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self.fwgrid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice1))
                self.fwgrid.SetCellAlignment(i, 1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self.fwgrid.SetCellEditor(i, 2, wx.grid.GridCellChoiceEditor(choices=portChoice3))
                self.fwgrid.SetCellAlignment(i, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self.fwgrid.SetCellEditor(i, 3, wx.grid.GridCellChoiceEditor(choices=portChoice4))
                self.fwgrid.SetCellAlignment(i, 3, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.fwgrid.SetRowLabelSize(30)
            self.fwgrid.SetRowLabelSize(1)

            '''确定按钮'''
            sure = wx.Button(self.panel, -1, '接口关系确认按钮', size=(200, 30))
            sure.SetFont(font2)
            self.Bind(wx.EVT_BUTTON, self.OnSureFwPorts, sure)

            # DNS1, 2
            dns1Static = wx.StaticText(self.panel, -1, 'DNS1:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
            dns2Static = wx.StaticText(self.panel, -1, '   DNS2:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
            self.dns1Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
            self.dns2Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
            self.dns1Text.AppendText(self.dns1)
            self.dns2Text.AppendText(self.dns2)
            dns1Static.SetFont(font)
            dns2Static.SetFont(font)
            box2 = wx.BoxSizer()
            box2.Add(dns1Static)
            box2.Add(self.dns1Text)
            box2.Add(dns2Static)
            box2.Add(self.dns2Text)

            # option
            optionStatic = wx.StaticText(self.panel, -1, 'Option:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
            optionStatic.SetFont(font)
            self.options = ['', '43', '148', '43 & 148']
            option = wx.Choice(self.panel, -1, choices=self.options, size=(100, 30), style=wx.LB_MULTIPLE)
            option.SetSelection(0)
            option.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
            self.Bind(wx.EVT_CHOICE, self.optionChoice, option)
            AC1Static = wx.StaticText(self.panel, -1, '   AC1:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
            AC1Static.SetFont(font)
            self.swAC1Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
            AC1Static2 = wx.StaticText(self.panel, -1, '   AC2:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
            AC1Static2.SetFont(font)
            self.swAC2Text = wx.TextCtrl(self.panel, size=(180, 30), style=wx.TE_CENTER)
            # print(self.options.index(self.optiontextvalue))
            option.SetSelection(self.options.index(self.optiontextvalue))
            self.swAC1Text.SetValue(self.ac1textvalue)
            self.swAC2Text.SetValue(self.ac2textvalue)
            if self.optionSelect == '':
                self.swAC1Text.Disable()
                self.swAC2Text.Disable()
            else:
                self.swAC1Text.Enable()
                self.swAC2Text.Enable()
            box3 = wx.BoxSizer()
            box3.Add(optionStatic)
            box3.Add(option)
            box3.Add(AC1Static)
            box3.Add(self.swAC1Text)
            box3.Add(AC1Static2)
            box3.Add(self.swAC2Text)
            mainSizer1.Add(box3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
            mainSizer1.Add(box2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
            mainSizer1.Add(self.fwgrid, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
            mainSizer1.Add(sure, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.panel.SetSizer(mainSizer1)
        mainSizer1.SetMinSize((1100 + self.page[self.i], 600))
        mainSizer1.Fit(self)

    def OnSureFwPorts(self, event):
        self.dns1 = self.dns1Text.GetValue()
        self.dns2 = self.dns2Text.GetValue()
        self.ac1textvalue = self.swAC1Text.GetValue()
        self.ac2textvalue = self.swAC2Text.GetValue()
        self.optiontextvalue = self.optionSelect
        if self.optionSelect == '':
            self.option = ''
        elif self.optionSelect == '43':
            self.option = 'dhcp server option 43 sub-option 2 ip-address ' + self.swAC1Text.GetValue() + ' ' +self.swAC2Text.GetValue()
        elif self.optionSelect == '148':
            self.option = 'dhcp server option 148 ascii agilemode=agile-cloud;agilemanage-mode=domain;agilemanage-domain=device-naas1.huawei.com;agilemanage-port=10020;'
        else:
            self.option = 'dhcp server option 43 sub-option 2 ip-address ' + self.swAC1Text.GetValue() + ' ' + self.swAC2Text.GetValue() + '\n'
            self.option = ' dhcp server option 148 ascii agilemode=agile-cloud;agilemanage-mode=domain;agilemanage-domain=device-naas1.huawei.com;agilemanage-port=10020;'
        for i in range(len(self.acFiles)):
            self.fwPortConnect[i]['0'] = self.fwgrid.GetCellValue(i, 0)
            self.fwPortConnect[i]['1'] = self.fwgrid.GetCellValue(i, 1)
            self.fwPortConnect[i]['2'] = self.fwgrid.GetCellValue(i, 2)
            self.fwPortConnect[i]['mad'] = self.fwgrid.GetCellValue(i, 3)
        for port in self.fwPortConnect:
            # print(port)
            if port['0'] != '' and port['1'] != '' and port['2'] != '':
                self.updownConnect.append(port['2'])
            elif port['0'] != '' and port['1'] == '' and port['2'] == '':
                self.updownConnect.append(port['0'])
            elif port['0'] == '' and port['1'] != '' and port['2'] == '':
                self.updownConnect.append(port['1'])
        self.updownConnect = list(set(self.updownConnect))

    def ACUI(self, event):
        self.i += 1
        if self.i > 5:
            self.i = 0
        self.panel.Destroy()

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        p = 0
        p1 = 0
        acFileButtons0 = wx.BoxSizer()
        if not self.acPortConnects:
            self.acPortConnects = []
            for i in range(len(self.acFiles)):
                if str(self.acFiles[i]['stackNumber']).strip() == '不堆叠':
                    self.acPortConnects.append({'sysname':self.acFiles[i]['sysname'], 'acPortConnect':[{'0':'', '1':'', '2':'', '3':'', '4':''}, {'0':'', '1':'', '2':'', '3':'', '4':''},{'0': '', '1': '','2': '', '3': '','4': ''},
                                                                                                       {'0': '', '1': '','2': '', '3': '','4': ''},{'0': '', '1': '','2': '', '3': '','4': ''},{'0': '', '1': '','2': '', '3': '','4': ''}
                                                                             , {'0': '', '1': '','2': '', '3': '','4': ''}, {'0': '', '1': '','2': '', '3': '','4': ''}]})
                else:
                    self.acPortConnects.append({'sysname': self.acFiles[i]['sysname'], 'acPortConnect': []})
                    for j in range(int(self.acFiles[i]['stackNumber'])):
                        if 'S2720' in self.acFiles[i]['sysname'].upper():
                            self.acPortConnects[-1]['acPortConnect'].append({'0': 'GigabitEthernet' + str(j + 1) + '/0/10', '1': '','2': '上行(ETH-TRUNK1)', '3': '','4': ''})
                        elif 'S2750' in self.acFiles[i]['sysname'].upper():
                            self.acPortConnects[-1]['acPortConnect'].append({'0': 'GigabitEthernet' + str(j + 1) + '/0/4', '1': '', '2': '上行(ETH-TRUNK1)', '3': '','4': ''})
                        elif 'S5720' in self.acFiles[i]['sysname'].upper():
                            self.acPortConnects[-1]['acPortConnect'].append({'0': 'GigabitEthernet' + str(j + 1) + '/0/48', '1': '', '2': '上行(ETH-TRUNK1)', '3': '','4': ''})
                    for j in range(int(self.acFiles[i]['stackNumber']), 8):
                        self.acPortConnects[-1]['acPortConnect'].append({'0': '', '1': '','2': '', '3': '','4': ''})
                self.updownConnectAc.append({'sysname':self.acFiles[i]['sysname'], 'port':[]})

        for i in range(len(self.acFiles)):
            temp = 'acFileButton%s=wx.Button(self.panel, -1, "%s", size=(250, 33))' % (str(i), self.acFiles[i]['sysname'])
            temp1 = 'acFileButtons%s.Add(acFileButton%s, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=2)' % (str(p1),str(i))
            temp2 = 'self.Bind(wx.EVT_BUTTON, self.dealAcFileButtons, acFileButton%s)' % str(i)
            p += 1
            if p == 5:
                p = 0
                p1 += 1
                exec('acFileButtons%s = wx.BoxSizer()' % p1)
            exec(temp)
            exec(temp1)
            exec(temp2)

        '''AC接入表格'''
        self.acgrid = wx.grid.Grid(self.panel, -1)
        self.acgrid.CreateGrid(8, 5)
        self.acgrid.SetGridCursor((8, 5))
        self.acgrid.SetColLabelValue(0, '开始端口')
        self.acgrid.SetColLabelValue(1, '结束端口')
        self.acgrid.SetColLabelValue(2, '用途')
        self.acgrid.SetColLabelValue(3, '互联设备')
        self.acgrid.SetColLabelValue(4, '互联端口')
        for i in range(0, 5):
            self.acgrid.SetColSize(i, 200)
        for i in range(0, 8):
            self.acgrid.SetRowSize(i, 30)
            self.acgrid.SetCellAlignment(i, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.acgrid.SetCellAlignment(i, 1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.acgrid.SetCellAlignment(i, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.acgrid.SetCellAlignment(i, 3, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.acgrid.SetCellAlignment(i, 4, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.acgrid.SetRowLabelSize(30)
        self.acgrid.SetRowLabelSize(1)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGED, self.OnChangeGrid, self.acgrid)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        '''确定按钮'''
        sure = wx.Button(self.panel, -1, '端口确认按钮', size=(200, 30))
        sure.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.OnSureAcPorts, sure)

        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
        else:
            button2.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()

        # ACsysname
        sysNameStatic = wx.StaticText(self.panel, -1, '设备名称:    ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.acSysname = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        manageIpStatic = wx.StaticText(self.panel, -1, '  管理IP:    ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.manageIp = wx.TextCtrl(self.panel, size=(130, 30), style=wx.TE_CENTER | wx.TE_READONLY)
        sysNameStatic.SetFont(font)
        manageIpStatic.SetFont(font)
        box1 = wx.BoxSizer()
        box1.Add(sysNameStatic)
        box1.Add(self.acSysname)
        box1.Add(manageIpStatic)
        box1.Add(self.manageIp)

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        for i in range(p1+1):
            exec('mainSizer1.Add(acFileButtons%s, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=2)'%str(i))
        mainSizer1.Add(box1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(self.acgrid, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(sure, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.panel.SetSizer(mainSizer1)
        mainSizer1.SetMinSize((1100 + self.page[self.i], 600 + self.page[self.i]))
        mainSizer1.Fit(self)

    def OnSureAcPorts(self, event):
        if self.acprev == '':
            pass
        else:
            for i in range(len(self.acPortConnects)):
                if self.acPortConnects[i]['sysname'] == self.acprev:
                    for j in range(8):
                        self.acPortConnects[i]['acPortConnect'][j]['0'] = self.acgrid.GetCellValue(j, 0)
                        self.acPortConnects[i]['acPortConnect'][j]['1'] = self.acgrid.GetCellValue(j, 1)
                        self.acPortConnects[i]['acPortConnect'][j]['2'] = self.acgrid.GetCellValue(j, 2)
                        self.acPortConnects[i]['acPortConnect'][j]['3'] = self.acgrid.GetCellValue(j, 4)
                        self.acPortConnects[i]['acPortConnect'][j]['4'] = self.acgrid.GetCellValue(j, 3)
            for i in range(len(self.updownConnectAc)):
                if self.updownConnectAc[i]['sysname'] == self.acprev:
                    # print(self.updownConnectAc)
                    for j in range(8):
                        if '单线' in self.acgrid.GetCellValue(j, 2):
                            self.updownConnectAc[i]['port'].append(self.acgrid.GetCellValue(j, 0))
                            self.updownConnectAc[i]['port'] = list(set(self.updownConnectAc[i]['port']))

        for i in range(len(self.acPortConnects)):
            for port in self.acPortConnects[i]['acPortConnect']:
                # print(port)
                if port['3'] != '':
                    for j in range(len(self.swPortConnect)):
                        if self.swPortConnect[j]['2'] == port['3']:
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.swPortConnect[j]['3'] = port
                        elif self.swPortConnect[j]['2'] == '' and self.swPortConnect[j]['0'] == port['3'] and self.swPortConnect[j]['1'] == '':
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.swPortConnect[j]['3'] = port
                        elif self.swPortConnect[j]['2'] == '' and self.swPortConnect[j]['1'] == port['3'] and self.swPortConnect[j]['0'] == '':
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.swPortConnect[j]['3'] = port

                    for j in range(len(self.fwPortConnect)):
                        if self.fwPortConnect[j]['2'] == port['3']:
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.fwPortConnect[j]['3'] = port
                        elif self.fwPortConnect[j]['2'] == '' and self.fwPortConnect[j]['0'] == port['3'] and self.fwPortConnect[j]['1'] == '':
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.fwPortConnect[j]['3'] = port
                        elif self.fwPortConnect[j]['2'] == '' and self.fwPortConnect[j]['1'] == port['3'] and self.fwPortConnect[j]['0'] == '':
                            port['sysname'] = self.acPortConnects[i]['sysname']
                            self.fwPortConnect[j]['3'] = port
        # print(self.updownConnect)
        # print(self.fwPortConnect)

    def dealAcFileButtons(self, event):
        # for acFile in self.acFiles:
        #     print(acFile['sysname'], acFile['stackNumber'])
        ID = event.GetEventObject().GetLabel()
        ID = ID.upper()
        self.acSysname.SetValue(ID)
        acsysnames = []
        for ac in self.acFiles:
            if ac['sysname'] != '':
                acsysnames.append(ac['sysname'])
        acsysnames.remove(ID)

        for ac in self.acFiles:
            if ac['sysname'] == ID:
                self.manageIp.SetValue(ac['manageIp'])
                if str(ac['stackNumber']).strip() == '不堆叠':
                    ppp = 0
                else:
                    ppp = int(str(ac['stackNumber']).strip())
                    # print(ppp)
                break

        self.acprev = ID
        purposeChoice = ['', '有线', '无线(友商)', '无线(华为)', '直播/培训', '安防', '其他', '上行(ETH-TRUNK1)', '单线上联', '单线下联']
        for i in range(ppp):
            self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellTextEditor())
            self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellTextEditor())
        for i in range(ppp, 8):
            self.acgrid.SetCellEditor(i, 2, wx.grid.GridCellChoiceEditor(choices=purposeChoice))
        if 'S2700' in ID:
            portChoice = [''] + ['Ethernet0/0/' + str(i) for i in range(1, 25)] + ['GigabitEthernet0/0/' + str(i) for i in range(1, 3)]
            for i in range(ppp):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellTextEditor())
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellTextEditor())
            for i in range(ppp, 8):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice))
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice))
        elif 'S2720' in ID:
            portChoice = [''] + ['Ethernet0/0/' + str(i) for i in range(1, 17)] + ['GigabitEthernet0/0/' + str(i) for i in range(1, 11)]
            for i in range(ppp):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellTextEditor())
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellTextEditor())
            for i in range(ppp, 8):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice))
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice))
        elif 'S2750' in ID:
            portChoice = [''] + ['Ethernet0/0/' + str(i) for i in range(1, 25)] + ['GigabitEthernet0/0/' + str(i) for i in range(3, 5)]
            for i in range(ppp):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellTextEditor())
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellTextEditor())
            for i in range(ppp, 8):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice))
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice))
        elif 'S5720' in ID:
            portChoice = [''] + ['GigabitEthernet0/0/' + str(i) for i in range(1, 49)] + ['XGigabitEthernet0/0/' + str(i) for i in range(1, 5)]
            for i in range(ppp):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellTextEditor())
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellTextEditor())
            for i in range(ppp, 8):
                self.acgrid.SetCellEditor(i, 0, wx.grid.GridCellChoiceEditor(choices=portChoice))
                self.acgrid.SetCellEditor(i, 1, wx.grid.GridCellChoiceEditor(choices=portChoice))
        for i in range(0, 8):
            self.acgrid.SetCellEditor(i, 4, wx.grid.GridCellChoiceEditor(choices=self.updownConnect))
        for i in range(0, 8):
            self.acgrid.SetCellEditor(i, 3, wx.grid.GridCellChoiceEditor(choices=['' , '核心/防火墙'] + acsysnames))
        for i in range(len(self.acPortConnects)):
            if self.acPortConnects[i]['sysname'] == self.acprev:
                for j in range(8):
                    self.acgrid.SetCellValue(j, 0, self.acPortConnects[i]['acPortConnect'][j]['0'])
                    self.acgrid.SetCellValue(j, 1, self.acPortConnects[i]['acPortConnect'][j]['1'])
                    self.acgrid.SetCellValue(j, 2, self.acPortConnects[i]['acPortConnect'][j]['2'])
                    self.acgrid.SetCellValue(j, 4, self.acPortConnects[i]['acPortConnect'][j]['3'])
                    self.acgrid.SetCellValue(j, 3, self.acPortConnects[i]['acPortConnect'][j]['4'])

    def OutPutUI(self, event):
        self.i += 1
        if self.i > 5:
            self.i = 0
        self.panel.Destroy()

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        sure = wx.Button(self.panel, -1, '文件生成确认按钮', size=(200, 30))
        sure.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.OnSureCreateFiles, sure)

        # 选择生成文件格式
        fileClassStatic = wx.StaticText(self.panel, -1, '生成文件格式:  ', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        fileClassStatic.SetFont(font)
        fileClassChoice = wx.Choice(self.panel, -1, choices=['Txt', 'Cfg'], size=(80, 30))
        fileClassChoice.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        fileClassChoice.SetSelection(0)
        box1 = wx.BoxSizer()
        box1.Add(fileClassStatic)
        box1.Add(fileClassChoice)

        '''主界面上的按钮'''
        button = wx.Button(self.panel, -1, '加载源数据', size=(150, 33))
        button2 = wx.Button(self.panel, -1, "核心", size=(150, 33))
        button3 = wx.Button(self.panel, -1, "防火墙", size=(150, 33))
        button4 = wx.Button(self.panel, -1, "接入", size=(150, 33))
        button5 = wx.Button(self.panel, -1, "输出", size=(150, 33))
        button.SetFont(font2)
        button2.SetFont(font2)
        button3.SetFont(font2)
        button4.SetFont(font2)
        button5.SetFont(font2)
        self.Bind(wx.EVT_BUTTON, self.firstPage, button)
        self.Bind(wx.EVT_BUTTON, self.SWUI, button2)
        self.Bind(wx.EVT_BUTTON, self.FWUI, button3)
        self.Bind(wx.EVT_BUTTON, self.ACUI, button4)
        self.Bind(wx.EVT_BUTTON, self.OutPutUI, button5)
        UIButton = wx.BoxSizer()
        UIButton.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button4, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        UIButton.Add(button5, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        if 'D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper():
            button2.Disable()
        else:
            button2.Enable()
        if self.fwYN == '无FW':
            button3.Disable()
        elif ('D' in self.bussniessClass.upper() or 'E' in self.bussniessClass.upper() ) and self.fwYN == '无FW':
            button3.Disable()
        else:
            button3.Enable()

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(UIButton, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(box1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(sure, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel.SetSizer(mainSizer1)

        mainSizer1.SetMinSize((1100 + self.page[self.i], 600))
        mainSizer1.Fit(self)

    def OnSureCreateFiles(self, event):
        # print(self.acFiles)
        # print(self.acPortConnects)
        # print(self.fwPortConnect)
        print(self.fwFile)
        print(self.acFiles)
        print(self.swFile)
        if self.fwFile != '':
            # print(self.fwFile)
            if 'D' in self.bussniessClass or 'E' in self.bussniessClass:
                dealFwFile.dealDE(self.fwFile, self.ipPlans, self.fwPortConnect, self.dns1, self.dns2, self.option)
            else:
                dealFwFile.dealABC(self.fwFile, self.ipPlans)
        if self.swFile != '':
            # print(self.swFile)
            dealSwFile.dealSw(self.swFile, self.ipPlans, self.swPortConnect, self.dns1, self.dns2, self.option)
        if self.acFiles != '':
            dealAcFile.dealAcs(self.acFiles, self.acPortConnects, self.ipPlans, [device for device in self.devices if '接入' in device['deviceRole']])
        easygui.msgbox('生成文件完成')

    def OnChangeGrid(self, event):
        for i in range(0, 8):
            if self.acgrid.GetCellValue(i, 3) == '核心/防火墙':
                self.acgrid.SetCellEditor(i, 4, wx.grid.GridCellChoiceEditor(choices=self.updownConnect))
            elif self.acgrid.GetCellValue(i, 3) == '':
                self.acgrid.SetCellEditor(i, 4, wx.grid.GridCellChoiceEditor(choices=['']))
            else:
                for j in range(len(self.updownConnectAc)):
                    if self.updownConnectAc[j]['sysname'] == self.acgrid.GetCellValue(i, 3):
                        self.acgrid.SetCellEditor(i, 4, wx.grid.GridCellChoiceEditor(choices=self.updownConnectAc[j]['port']))

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame('平安脚本工具')
    frame.Show()
    app.MainLoop()
