import xlwt
import os
import wx
import re
import easygui

j = 1
#设置居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER  #水平方向
alignment.vert = xlwt.Alignment.VERT_TOP  #垂直方向

# 设置背景色
pattern = xlwt.Pattern() # Create the Pattern
pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
pattern.pattern_fore_colour = 17

workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('My Sheet')

style = xlwt.XFStyle() # Create the Pattern
style.pattern = pattern # Add Pattern to Style
style.alignment = alignment

style1 = xlwt.XFStyle()
style1.alignment = alignment

# 第一行参数
worksheet.write(0, 0, '序号', style)
worksheet.write(0, 1, '设备名称', style)
worksheet.write(0, 2, '管理IP地址', style)
worksheet.write(0, 3, '设备类型', style)
worksheet.write(0, 4, '机框SN', style)
worksheet.write(0, 5, '板卡SN（可选）', style)
worksheet.write(0, 6, '电源SN（可选）', style)
worksheet.write(0, 7, '风扇SN（可选）', style)
worksheet.write(0, 8, '光模板SN（可选）', style)

# 设置单元格长度
worksheet.col(0).width = 0x0a00
worksheet.col(1).width = 0x0d00 + 100*50
worksheet.col(2).width = 0x0d00
worksheet.col(3).width = 0x0d00 + 30*50
worksheet.col(4).width = 0x0d00 + 60*50
worksheet.col(5).width = 0x0d00 + 50*50
worksheet.col(6).width = 0x0d00 + 50*50
worksheet.col(7).width = 0x0d00 + 50*50
worksheet.col(8).width = 0x0d00 + 60*50

class MyFrame(wx.Frame):
    def __init__(self,title):
        self.checkList = []
        wx.Frame.__init__(self, None, -1, title, size=(700, 220))
        self.panel = wx.Panel(self)
        font = wx.Font(20, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''脚本文件夹选择'''
        btnSizerStatic1 = wx.StaticText(self.panel, -1, '脚本文件夹地址:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.scriptPath = wx.TextCtrl(self.panel, size=(300, 30), style=wx.TE_MULTILINE)
        btnSizerStatic1.SetFont(font)
        button6 = wx.Button(self.panel, -1, '打开', size=(70, 30))
        button7 = wx.Button(self.panel, -1, '清除', size=(70, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton6, button6)
        self.Bind(wx.EVT_BUTTON, self.OnButton7, button7)
        dirSizer1 = wx.BoxSizer()
        dirSizer1.Add(btnSizerStatic1)
        dirSizer1.Add(self.scriptPath)
        dirSizer1.Add(button6, proportion=0)
        dirSizer1.Add(button7, proportion=0)

        '''多选框'''
        # checkStatic = wx.StaticText(self.panel, -1, '选择要获取的SN:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        check1 = wx.CheckBox(self.panel, -1, '板卡SN', size=(200, 20))
        check1.SetFont(wx.Font(15, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        check2 = wx.CheckBox(self.panel, -1, '电源SN', size=(200, 20))
        check2.SetFont(wx.Font(15, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        check3 = wx.CheckBox(self.panel, -1, '风扇SN', size=(200, 20))
        check3.SetFont(wx.Font(15, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        check4 = wx.CheckBox(self.panel, -1, '光模块SN', size=(200, 20))
        check4.SetFont(wx.Font(15, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        self.Bind(wx.EVT_CHECKBOX, self.checkBox, check1)
        self.Bind(wx.EVT_CHECKBOX, self.checkBox, check2)
        self.Bind(wx.EVT_CHECKBOX, self.checkBox, check3)
        self.Bind(wx.EVT_CHECKBOX, self.checkBox, check4)

        '''确定按钮'''
        button5 = wx.Button(self.panel, -1, '确定', size=(100, 20))
        self.Bind(wx.EVT_BUTTON, self.OnButton5, button5)

        '''界面竖向排列下去'''
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(dirSizer1, proportion=-1, flag = wx.CENTER)
        mainSizer1.Add(check1, proportion=-1, flag=wx.CENTER)
        mainSizer1.Add(check2, proportion=-1, flag=wx.CENTER)
        mainSizer1.Add(check3, proportion=-1, flag=wx.CENTER)
        mainSizer1.Add(check4, proportion=-1, flag=wx.CENTER)
        mainSizer1.Add(button5, proportion=-1, flag=wx.CENTER)
        self.panel.SetSizer(mainSizer1)
        self.Center()
        self.Show()

    def checkBox(self, event):
        checkBoxSelect = event.GetEventObject()
        if checkBoxSelect.IsChecked():
            self.checkList.append(checkBoxSelect.GetLabelText())
        else:
            self.checkList.remove(checkBoxSelect.GetLabelText())

    def OnButton6(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.scriptPath.AppendText(dlg.GetPath())
        dlg.Destroy()

    def OnButton7(self, event):
        self.scriptPath.Clear()

    def OnButton5(self, event):
        global arr
        BKSNIF = DYSNIF = FSSNIF = GMKSNIF = False
        if '光模块SN' in self.checkList:
            GMKSNIF = True
        if '板卡SN' in self.checkList:
            BKSNIF = True
        if '电源SN' in self.checkList:
            DYSNIF = True
        if '风扇SN' in self.checkList:
            FSSNIF = True
        arr = [self.scriptPath.GetValue(), BKSNIF , DYSNIF , FSSNIF , GMKSNIF]
        self.Close(True)

if __name__ == '__main__':
    app = wx.App()
    MyFrame('获取SN初始值选择框')
    app.MainLoop()
    filePath, BKSNIF, DYSNIF, FSSNIF, GMKSNIF = arr

    files = os.listdir(filePath)
    files = [os.path.join(filePath, file) for file in files]

    flag = False
    for file in files:
        snAllInfo = []
        jksn = ''
        with open(file, 'rb') as f:
            for line in f:
                if re.search('<[\s\S]*?>', line.decode('utf8', 'ignore')):
                    flag = False
                if flag:
                    if 'Equipment SN(ESN)' in line.decode('utf8', 'ignore'):
                        jksn = line.decode('utf8', 'ignore').split(':')[-1].strip()
                        continue
                    if jksn != '':
                        if re.search('1[\s\S]*?-([\s\S]*?)' + jksn, line.decode('utf8', 'ignore')) :
                            deviceType = re.search('1[\s\S]*?-([\s\S]*?)' + jksn, line.decode('utf8', 'ignore')) .groups()[0].strip()
                            continue
                        if re.search('BackPlane', line.decode('utf8', 'ignore')):
                            deviceType = 'CE12816-AC'
                    snAllInfo.append(line.decode('utf8', 'ignore'))
                if 'dissnall' in re.sub(' ', '', line.decode('utf8', 'ignore')):
                    deviceName = re.search('<([\s\S]*?)>', line.decode('utf8', 'ignore')).groups()[0]
                    flag = True

        worksheet.write(j, 0, j, style1)
        worksheet.write(j, 1, deviceName, style1)
        worksheet.write(j, 2, '--', style1)
        worksheet.write(j, 3, deviceType, style1)
        worksheet.write(j, 4, jksn, style1)

        if BKSNIF:  # 5
            bksn = []
            for info in snAllInfo:
                if jksn not in info and not re.search('PWR', info) and not re.search('FAN', info) and not re.search('\dGE\d/\d/\d', info):
                    if re.search('^\d[\S\s]*?--[\S\s]*?\n', info):
                        info = [i for i in info.split(' ') if re.search('\S', i)]
                        bksn.append(info[-2])
            if bksn:
                worksheet.write(j, 5, ';'.join(bksn), style1)
            else:
                worksheet.write(j, 5, '--', style1)
        else:
            worksheet.write(j, 5, '--', style1)

        if DYSNIF:  # 6
            dysn = []
            for info in snAllInfo:
                if re.search('PWR\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    dysn.append(info[-2])
            if dysn:
                worksheet.write(j, 6, ';'.join(dysn), style1)
            else:
                worksheet.write(j, 6, '--', style1)
        else:
            worksheet.write(j, 6, '--', style1)

        if FSSNIF:  # 7
            fssn = []
            for info in snAllInfo:
                if re.search('FAN\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    fssn.append(info[-2])
            if fssn:
                worksheet.write(j, 7, ';'.join(fssn), style1)
            else:
                worksheet.write(j, 7, '--', style1)
        else:
            worksheet.write(j, 7, '--', style1)

        if GMKSNIF:  # 8
            gmksn = []
            for info in snAllInfo:
                if re.search('\dGE\d/\d/\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    if info[2] != '--':
                        gmksn.append(info[2])
            if gmksn:
                worksheet.write(j, 8, ';'.join(gmksn), style1)
            else:
                worksheet.write(j, 8, '--', style1)
        else:
            worksheet.write(j, 8, '--', style1)
        j += 1

workbook.save('采集SN信息.xls')
easygui.msgbox('提取SN作业完成')