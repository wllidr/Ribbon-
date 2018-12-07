'''
    Date : 2018 - 12 - 06
    Author : Ribbon Huang
    Desc:
        集成各种网络小工具于一体
'''
import wx
import sys
sys.path.append('.')
import autoscript
import ipscan
import autotemplate
import getpeer
import fabfile
import getvnibd

class AutoTools(wx.Frame):
    def __init__(self,parent,title):
        # 面板初始参数
        self.panel = self.panel1 = self.panel2 = self.panel3 = self.panel4 = self.panel5 = None

        wx.Frame.__init__(self,parent,title=title,size=(600, 350))
        self.CreateStatusBar()# 创建位于窗口的底部的状态栏

        filemenu = wx.Menu()  #设置菜单
        menuAutoScript = filemenu.Append(wx.ID_FILE1, "&自动刷脚本", "自动刷脚本配置，并且生成日志文件")
        menuIpCheck = filemenu.Append(wx.ID_FILE, "&IP检测器", "用于检测IP是否连通以及在连通后尝试ssh获取设备名，并生成表格")
        menuVniDd = filemenu.Append(wx.ID_ABOUT,"&VNI以及BD号提取", "用于VNI以及BD号提取，并生成表格")
        menutemplate = filemenu.Append(wx.ID_FILE3, "&自动模板配置生成", "根据模板批量生产配置")
        menupeer = filemenu.Append(wx.ID_FILE5, "&获取peer参数", "获取peer的参数，并且形成表格...")
        menufileupdown = filemenu.Append(wx.ID_FILE7, "&服务器文件上传下载", "对服务器文件进行上传下载操作， 并且执行fabscript.txt的脚本....")
        filemenu.AppendSeparator()  #分割线
        menuExit = filemenu.Append(wx.ID_EXIT,"&退出","退出后界面将关闭") # 退出按钮，整个系统退出

        #创建菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&功能选择") #在菜单栏中添加filemenu菜单
        self.SetMenuBar(menuBar) #在frame中添加菜单栏

        #设置 events
        self.Bind(wx.EVT_MENU, self.OnAutoScript, menuAutoScript)
        self.Bind(wx.EVT_MENU, self.OnIpCheck, menuIpCheck)
        self.Bind(wx.EVT_MENU, self.OnVniBdExtract, menuVniDd)
        self.Bind(wx.EVT_MENU, self.OntemplateProduce, menutemplate)
        self.Bind(wx.EVT_MENU, self.OnPeerGet, menupeer)
        self.Bind(wx.EVT_MENU, self.OnFileUpDown, menufileupdown)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Center()
        self.Show()

    '''自动化刷脚本panel界面图 self.panel'''
    def OnAutoScript(self, event):
        if self.panel1:
            self.panel1.Destroy()
        if self.panel2:
            self.panel2.Destroy()
        if self.panel3:
            self.panel3.Destroy()
        if self.panel4:
            self.panel4.Destroy()
        if self.panel5:
            self.panel5.Destroy()
        if self.panel:
            self.panel1 = self.panel2 = self.panel3 = self.panel4 = self.panel5 = None
            return
        self.checkVarible = True
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''选择EXcel的地址选择框'''
        excelStticText = wx.StaticText(self.panel, -1, 'excel表格地址:')
        self.excelPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        excelStticText.SetFont(font)
        button1 = wx.Button(self.panel, -1, '打开', size=(60, 30))
        button2 = wx.Button(self.panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton1, button1)
        self.Bind(wx.EVT_BUTTON, self.OnButton2, button2)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(excelStticText)
        btnSizer.Add(self.excelPath)
        btnSizer.Add(button1)
        btnSizer.Add(button2)

        '''脚本文件夹路径选择框'''
        dirStaticText = wx.StaticText(self.panel, -1, '脚本文件夹地址:')
        self.scriptPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        dirStaticText.SetFont(font)
        button3 = wx.Button(self.panel, -1, '打开', size=(60, 30))
        button4 = wx.Button(self.panel, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton3, button3)
        self.Bind(wx.EVT_BUTTON, self.OnButton4, button4)
        dirSizer1 = wx.BoxSizer()
        dirSizer1.Add(dirStaticText)
        dirSizer1.Add(self.scriptPath)
        dirSizer1.Add(button3)
        dirSizer1.Add(button4)

        '''线程数'''
        poolNumberStatic = wx.StaticText(self.panel, -1, '线程数(填数字):')
        self.poolNumber = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        poolNumberStatic.SetFont(font)
        button6 = wx.Button(self.panel, -1, '清除', size=(120, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton6, button6)
        numberSizer = wx.BoxSizer()
        numberSizer.Add(poolNumberStatic)
        numberSizer.Add(self.poolNumber)
        numberSizer.Add(button6)

        '''是否需要进行验证'''
        checkIf = wx.StaticText(self.panel, -1, '刷脚本时是否需要进行验证: ')
        checkIf.SetFont(font)
        self.choice = ['Yes', 'No']
        chooseCheckChoice = wx.Choice(self.panel, -1, choices=self.choice, size=(60, 30))
        chooseCheckChoice.SetFont(font)
        self.Bind(wx.EVT_CHOICE, self.radioCh, chooseCheckChoice)
        chooseCheckChoice.SetSelection(0)
        radioCheck = wx.BoxSizer()
        radioCheck.Add(checkIf)
        radioCheck.Add(chooseCheckChoice)

        '''确定按钮'''
        button5 = wx.Button(self.panel, -1, '确定执行按钮', size=(120, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSure, button5)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText('1. 选择所需刷配置设备文件的Excel文档\n2. 选择Excel文件中刷配置文件的文件夹\n3. 写入刷配置的线程数（数字）\n4. 选择刷脚本是否需要验证，默认为需要验证\n5. 当以上参数确认无误，点击确认按钮开始刷配置')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(btnSizer, proportion=0,  flag=wx.ALIGN_RIGHT | wx.ALL, border= 5)
        mainSizer1.Add(dirSizer1, proportion=0,  flag=wx.ALIGN_RIGHT | wx.ALL, border= 5)
        mainSizer1.Add(numberSizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        mainSizer1.Add(radioCheck, proportion=0, flag=wx.CENTER | wx.ALL, border = 5)
        mainSizer1.Add(button5, proportion=0,  flag=wx.CENTER | wx.ALL,border= 5)
        mainSizer1.Add(operate, proportion=0, flag=wx.CENTER | wx.ALL, border=5)
        self.panel.SetSizer(mainSizer1)
        mainSizer1.SetMinSize((600, 350))
        mainSizer1.Fit(self)

    def OnButton1(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN )
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.excelPath.AppendText(fileDialog.GetPath())

    def OnButton2(self,event):
        self.excelPath.Clear()

    def OnButton3(self,event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.scriptPath.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton4(self, event):
        self.scriptPath.Clear()

    def EnSure(self, event):
        # print([self.excelPath.GetValue(), self.scriptPath.GetValue(), self.poolNumber.GetValue(), self.checkVarible])
        autoscript.autoScriptBegin(self.checkVarible, self.poolNumber.GetValue(), self.excelPath.GetValue(), self.scriptPath.GetValue())

    def radioCh(self, event):
        self.checkVarible = event.GetEventObject().GetSelection()
        if self.checkVarible == 1:
            self.checkVarible = False
        else:
            self.checkVarible = True

    def OnButton6(self, event):
        self.poolNumber.Clear()

    '''提取vni Bd号界面self.panel'''
    def OnVniBdExtract(self, event):
        if self.panel:
            self.panel.Destroy()
        if self.panel2:
            self.panel2.Destroy()
        if self.panel3:
            self.panel3.Destroy()
        if self.panel4:
            self.panel4.Destroy()
        if self.panel5:
            self.panel5.Destroy()
        if self.panel1:
            self.panel = self.panel2 = self.panel3 = self.panel4 = self.panel5 = None
            return
        self.panel1 = wx.Panel(self)
        self.panel1.SetBackgroundColour('white')
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''脚本文件夹路径选择框'''
        vniStaticText = wx.StaticText(self.panel1, -1, '脚本文件夹地址:')
        self.vniStaticPath = wx.TextCtrl(self.panel1, size=(300, 30), style=wx.TE_MULTILINE)
        vniStaticText.SetFont(font)
        button26 = wx.Button(self.panel1, -1, '打开', size=(60, 30))
        button27 = wx.Button(self.panel1, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton26, button26)
        self.Bind(wx.EVT_BUTTON, self.OnButton27, button27)
        dirSizer1 = wx.BoxSizer()
        dirSizer1.Add(vniStaticText)
        dirSizer1.Add(self.vniStaticPath)
        dirSizer1.Add(button26)
        dirSizer1.Add(button27)

        '''确定按钮'''
        button25 = wx.Button(self.panel1, -1, '确定执行按钮', size=(120, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSurePanel1, button25)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel1, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel1, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText(
            '1. 选择配置的文件夹\n2. 以上确认无误后，按确认开始执行程序\n4. 文件生成生成在‘自动生成文件文件夹’目录下的 VNIBDIP提取表格.xls')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(dirSizer1, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        mainSizer1.Add(button25, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer1.Add(operate, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel1.SetSizer(mainSizer1)
        mainSizer1.SetMinSize((600, 352))
        mainSizer1.Fit(self)

    def OnButton26(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.vniStaticPath.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton27(self, event):
        self.vniStaticPath.Clear()

    def EnSurePanel1(self, event):
        getvnibd.begin_vni_bd(self.vniStaticPath.GetValue())

    '''IP自动检测界面self.panel2'''
    def OnIpCheck(self, event):
        if self.panel:
            self.panel.Destroy()
        if self.panel1:
            self.panel1.Destroy()
        if self.panel3:
            self.panel3.Destroy()
        if self.panel4:
            self.panel4.Destroy()
        if self.panel5:
            self.panel5.Destroy()
        if self.panel2:
            self.panel = self.panel1 = self.panel3 = self.panel4 = self.panel5 = None
            return

        self.panel2 = wx.Panel(self)
        self.panel2.SetBackgroundColour('white')
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''选择EXcel的地址选择框'''
        excelStticText = wx.StaticText(self.panel2, -1, '模板表格地址:')
        self.ipCheckExcel = wx.TextCtrl(self.panel2, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        excelStticText.SetFont(font)
        button7 = wx.Button(self.panel2, -1, '打开', size=(60, 30))
        button8 = wx.Button(self.panel2, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton7, button7)
        self.Bind(wx.EVT_BUTTON, self.OnButton8, button8)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(excelStticText)
        btnSizer.Add(self.ipCheckExcel)
        btnSizer.Add(button7)
        btnSizer.Add(button8)

        '''确定按钮'''
        button9 = wx.Button(self.panel2, -1, '确定执行按钮', size=(120, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSurePanel2, button9)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel2, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel2, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText(
            '1. 参照工具表格模板中表‘IP检测器’的格式进行编辑Excel文档\n2. 选择第一步制作的Excel文档\n3. 以上确认无误后，按确认开始执行程序\n4. 文件生成生成在‘自动生成文件文件夹’目录下')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        mainSizer2 = wx.BoxSizer(wx.VERTICAL)
        mainSizer2.Add(btnSizer, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer2.Add(button9, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer2.Add(operate, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel2.SetSizer(mainSizer2)
        mainSizer2.SetMinSize((600, 351))
        mainSizer2.Fit(self)

    def OnButton7(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.ipCheckExcel.AppendText(fileDialog.GetPath())

    def OnButton8(self, event):
        self.ipCheckExcel.Clear()

    def EnSurePanel2(self, event):
        ipscan.begin_ip_scan(self.ipCheckExcel.GetValue())

    '''自动模板配置生成器self.panel3'''
    def OntemplateProduce(self, event):
        if self.panel:
            self.panel.Destroy()
        if self.panel1:
            self.panel1.Destroy()
        if self.panel2:
            self.panel2.Destroy()
        if self.panel4:
            self.panel4.Destroy()
        if self.panel5:
            self.panel5.Destroy()
        if self.panel3:
            self.panel = self.panel1 = self.panel2 = self.panel4 = self.panel5 = None
            return

        self.panel3= wx.Panel(self)
        self.panel3.SetBackgroundColour('white')
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        excelStticText = wx.StaticText(self.panel3, -1, '模板表格地址:')
        self.templeteExcelPath = wx.TextCtrl(self.panel3, size=(300, 30), style=wx.TE_MULTILINE)
        excelStticText.SetFont(font)
        button9 = wx.Button(self.panel3, -1, '打开', size=(60, 30))
        button10 = wx.Button(self.panel3, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton9, button9)
        self.Bind(wx.EVT_BUTTON, self.OnButton10, button10)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(excelStticText)
        btnSizer.Add(self.templeteExcelPath)
        btnSizer.Add(button9)
        btnSizer.Add(button10)

        '''配置模板的选择'''
        templeteStatic = wx.StaticText(self.panel3, -1, '模板列的选择（A-Z）')
        templeteStatic.SetFont(font)
        self.templeteSelect = wx.TextCtrl(self.panel3, size=(300, 30), style=wx.TE_MULTILINE)
        button11 = wx.Button(self.panel3, -1, '清除', size=(120, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton11, button11)
        btnSizer1 = wx.BoxSizer()
        btnSizer1.Add(templeteStatic)
        btnSizer1.Add(self.templeteSelect)
        btnSizer1.Add(button11)

        '''配置生成文件夹的输入'''
        produceStatic = wx.StaticText(self.panel3, -1, '配置存放目录')
        produceStatic.SetFont(font)
        self.produceStaticSelect = wx.TextCtrl(self.panel3, size=(300, 30), style=wx.TE_MULTILINE)
        button12 = wx.Button(self.panel3, -1, '清除', size=(120, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton12, button12)
        btnSizer2 = wx.BoxSizer()
        btnSizer2.Add(produceStatic)
        btnSizer2.Add(self.produceStaticSelect)
        btnSizer2.Add(button12)

        '''确定按钮'''
        button13 = wx.Button(self.panel3, -1, '确定执行按钮', size=(120, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSureTemplate, button13)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel3, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel3, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText(
            '1. 参照工具表格模板中表’配置参数‘,’配置模板‘的格式进行编辑Excel文档\n2. 选择第一步制作的Excel文档\n3. 选择配置模板中所选择模板的行\n4. 输入由自动化工具生成文件的文件夹名称\n5. 以上确认无误后，按确认开始执行程序')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        mainSizer3 = wx.BoxSizer(wx.VERTICAL)
        mainSizer3.Add(btnSizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        mainSizer3.Add(btnSizer1, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        mainSizer3.Add(btnSizer2, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        mainSizer3.Add(button13, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer3.Add(operate, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel3.SetSizer(mainSizer3)
        mainSizer3.SetMinSize((600, 353))
        mainSizer3.Fit(self)

    def OnButton9(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.templeteExcelPath.AppendText(fileDialog.GetPath())

    def OnButton10(self, event):
        self.templeteExcelPath.Clear()

    def OnButton11(self, event):
        self.templeteSelect.Clear()

    def OnButton12(self, event):
        self.produceStaticSelect.Clear()

    def EnSureTemplate(self, event):
        # print(self.templeteExcelPath.GetValue(),self.templeteSelect.GetValue(),self.produceStaticSelect.GetValue())
        autotemplate.begin_template(self.templeteExcelPath.GetValue(),self.templeteSelect.GetValue(),self.produceStaticSelect.GetValue())

    '''获取peer'''
    def OnPeerGet(self, event):
        if self.panel:
            self.panel.Destroy()
        if self.panel1:
            self.panel1.Destroy()
        if self.panel2:
            self.panel2.Destroy()
        if self.panel3:
            self.panel3.Destroy()
        if self.panel5:
            self.panel5.Destroy()
        if self.panel4:
            self.panel = self.panel1 = self.panel2 = self.panel3 = self.panel5 = None
            return

        self.panel4 = wx.Panel(self)
        self.panel4.SetBackgroundColour('white')
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''选择peer所需文件夹地址'''
        excelStticText = wx.StaticText(self.panel4, -1, '配置文件夹:')
        self.peerDir = wx.TextCtrl(self.panel4, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        excelStticText.SetFont(font)
        button14 = wx.Button(self.panel4, -1, '打开', size=(60, 30))
        button15 = wx.Button(self.panel4, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton14, button14)
        self.Bind(wx.EVT_BUTTON, self.OnButton15, button15)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(excelStticText)
        btnSizer.Add(self.peerDir)
        btnSizer.Add(button14)
        btnSizer.Add(button15)

        '''确定按钮'''
        button16 = wx.Button(self.panel4, -1, '确定执行按钮', size=(120, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSurePanel4, button16)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel4, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel4, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText(
            '1. 选择要生成peer.xls相关参数的配置文件夹\n2. 生成的Excel放置在‘自动生成文件文件夹’目录下\n3. 以上确认无误后，按确认开始执行程序')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        mainSizer2 = wx.BoxSizer(wx.VERTICAL)
        mainSizer2.Add(btnSizer, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer2.Add(button16, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer2.Add(operate, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel4.SetSizer(mainSizer2)
        mainSizer2.SetMinSize((600, 354))
        mainSizer2.Fit(self)

    def OnButton14(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.peerDir.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton15(self, event):
        self.peerDir.Clear()

    def EnSurePanel4(self, event):
        getpeer.begin_peer(self.peerDir.GetValue())

    def OnFileUpDown(self, event):
        if self.panel:
            self.panel.Destroy()
        if self.panel1:
            self.panel1.Destroy()
        if self.panel2:
            self.panel2.Destroy()
        if self.panel3:
            self.panel3.Destroy()
        if self.panel4:
            self.panel4.Destroy()
        if self.panel5:
            self.panel = self.panel1 = self.panel2 = self.panel3 = self.panel4 = None
            return

        self.panel5 = wx.Panel(self)
        self.panel5.SetBackgroundColour('white')

        '''选择EXcel的地址选择框'''
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        excelStticText = wx.StaticText(self.panel5, -1, '上传下载表格:')
        self.fabupdown = wx.TextCtrl(self.panel5, size=(300, 30), style=wx.TE_MULTILINE | wx.TE_READONLY)
        excelStticText.SetFont(font)
        button20 = wx.Button(self.panel5, -1, '打开', size=(60, 30))
        button21 = wx.Button(self.panel5, -1, '清除', size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton20, button20)
        self.Bind(wx.EVT_BUTTON, self.OnButton21, button21)
        btnSizer = wx.BoxSizer()
        btnSizer.Add(excelStticText)
        btnSizer.Add(self.fabupdown)
        btnSizer.Add(button20)
        btnSizer.Add(button21)

        '''操作说明'''
        operateStatic = wx.StaticText(self.panel5, -1, '操作说明:')
        operateStatic.SetFont(font)
        operateInfo = wx.TextCtrl(self.panel5, size=(500, 120), style=wx.TE_MULTILINE | wx.TE_READONLY)
        operateInfo.AppendText(
            '1. 参照工具表格模板中表’服务器文件上传下载‘的格式进行编辑Excel文档\n2. 选择第一步制作的Excel文档\n3. 以上确认无误后，按确认开始执行程序\n4. 日志会生成在 自动生成文件文件夹\上传下载日志 下')
        font1 = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        operateInfo.SetFont(font1)
        operate = wx.BoxSizer()
        operate.Add(operateStatic)
        operate.Add(operateInfo)

        '''确定按钮'''
        button19 = wx.Button(self.panel5, -1, '确认工具表格模板中上传下载正确，请点击', size=(250, 33))
        self.Bind(wx.EVT_BUTTON, self.EnSurePanel5, button19)
        mainSizer5 = wx.BoxSizer(wx.VERTICAL)
        mainSizer5.Add(btnSizer, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer5.Add(button19, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer5.Add(operate, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.panel5.SetSizer(mainSizer5)
        mainSizer5.SetMinSize((600, 355))
        mainSizer5.Fit(self)

    def OnButton20(self, event):
        '''文件的选择'''
        filesFilter = "Excel(*.xls)|*.xls*|" "TXT(*.txt)|*.txt|" "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(self, message="确定打开文件", wildcard=filesFilter,
                                   style=wx.FD_OPEN)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        self.fabupdown.AppendText(fileDialog.GetPath())

    def OnButton21(self, event):
        self.fabupdown.Clear()

    def EnSurePanel5(self, event):
        fabfile.begin_fabfile(self.fabupdown.GetValue())

    def OnExit(self, event):
        # 关闭整个frame
        self.Close(True)

if __name__ == '__main__':
    app = wx.App()
    frame = AutoTools(None, title="招行网络小工具集成")
    app.MainLoop()
