import wx
import os

'''
    根据线路文件生成路程键值对格式
'''
wayInfo = {}
filePath = r'.\线路'
files = os.listdir(filePath)
files = [os.path.join(filePath, file) for file in files]
for file in files:
    with open(file, 'rb') as f:
        for line in f:
            line = line.decode('utf8')
            tempstart, tempend = line.split('\t')[0].split('——')
            distance = line.split('\t')[1]
            try:
                if wayInfo[tempstart]:
                    wayInfo[tempstart].update({tempend : int(distance)})
            except:
                    wayInfo[tempstart] = {tempend : int(distance)}
            try:
                if wayInfo[tempend]:

                    wayInfo[tempend].update({tempstart : int(distance)})
            except:
                    wayInfo[tempend] = {tempstart : int(distance)}

# 每次找到离源点最近的一个顶点，然后以该顶点为重心进行扩展
# 最终的到源点到其余所有点的最短路径
# 一种贪婪算法
def Dijkstra(wayInfo, startPoint, INF=float('inf')):
    """
        使用 Dijkstra 算法计算指定起始点 startPoint 到图 wayInfo 中任意点的最短路径的距离
        INF 为设定的无限远距离值
    """
    book = set()
    minv = startPoint

    # 源顶点到其余各顶点的初始路程， 除源点到源点以外都设置为INF
    dis = dict((k, INF) for k in wayInfo.keys())
    dis[startPoint] = 0   # 相同点则设置为0

    while len(book) < len(wayInfo):
        book.add(minv)  # 确定当期顶点的距离
        # print(book)
        for w in wayInfo[minv]:  # 以当前点的中心向外扩散
            if dis[minv] + wayInfo[minv][w] < dis[w]:  # 如果从当前点扩展到某一点的距离小与已知最短距离
                dis[w] = dis[minv] + wayInfo[minv][w]  # 对已知距离进行更新

        new = INF
        # 从剩下的未确定点中选择最小距离点作为新的扩散点
        for v in dis.keys():
            if v in book:
                continue
            if dis[v] < new:
                new = dis[v]
                minv = v
    return dis

class MyFrame(wx.Frame):
    '''
        界面，用于输入起始点和终点, 确定即可以出结果
    '''
    def __init__(self,title):
        self.checkList = []
        wx.Frame.__init__(self, None, -1, title, size=(700, 200))
        self.panel = wx.Panel(self)
        font = wx.Font(20, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        '''起始点输入框'''
        # 设置静态文本 ‘起点：’
        startStatic = wx.StaticText(self.panel, -1, '起点:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        # 设置起点输入框
        self.startPoint = wx.TextCtrl(self.panel, size=(150, 30), style=wx.TE_MULTILINE)
        # 设置静态文本 ‘起点：’字体大小、型号
        startStatic.SetFont(font)
        # 清除输入文本框按钮，按按钮清除则可以一次性清除
        button7 = wx.Button(self.panel, -1, '清除', size=(70, 30))
        self.Bind(wx.EVT_BUTTON, self.startButton, button7)

        # 将上面的起点、输入文本框、按钮放在一个Box里面来进行横向排版
        dirSizer1 = wx.BoxSizer()
        dirSizer1.Add(startStatic)
        dirSizer1.Add(self.startPoint)
        dirSizer1.Add(button7, proportion=0)

        '''终点输入框'''
        endStatic = wx.StaticText(self.panel, -1, '终点:', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        self.endPoint = wx.TextCtrl(self.panel, size=(150, 30), style=wx.TE_MULTILINE)
        endStatic.SetFont(font)
        button8= wx.Button(self.panel, -1, '清除', size=(70, 30))
        self.Bind(wx.EVT_BUTTON, self.endButton, button8)
        dirSizer2 = wx.BoxSizer()
        dirSizer2.Add(endStatic)
        dirSizer2.Add(self.endPoint)
        dirSizer2.Add(button8, proportion=0)

        '''人民币输出框'''
        self.rmb = wx.TextCtrl(self.panel, size=(200, 30), style=wx.CB_READONLY)
        # rmbStatic = wx.StaticText(self.panel, -1, '元', style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE)
        # rmbStatic.SetFont(font)
        button5 = wx.Button(self.panel, -1, '确定', size=(40, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButton5, button5)
        dirSizer3 = wx.BoxSizer()
        dirSizer3.Add(self.rmb)
        # dirSizer3.Add(rmbStatic)
        dirSizer3.Add(button5)

        '''界面竖向排列下去'''
        mainSizer1 = wx.BoxSizer(wx.VERTICAL)
        mainSizer1.Add(dirSizer1, proportion=-1, flag = wx.CENTER)
        mainSizer1.Add(dirSizer2, proportion=-1, flag=wx.CENTER)
        mainSizer1.Add(dirSizer3, proportion=-1, flag=wx.CENTER)
        # mainSizer1.Add(button5, proportion=-1, flag=wx.CENTER)
        self.panel.SetSizer(mainSizer1)
        self.Center()
        self.Show()

    def startButton(self, event):
        self.startPoint.Clear()

    def endButton(self, event):
        self.endPoint.Clear()

    def OnButton5(self, event):
        '''确定按钮获取路径计算钱数量'''
        self.rmb.Clear()
        try:
            # 调用Dijkstra函数
            disAll = Dijkstra(wayInfo, startPoint=self.startPoint.GetValue())
            print(disAll)
        except:
            self.rmb.AppendText('没有该起点，请重新确认')
            return None
        try:
            distance = disAll[self.endPoint.GetValue()]
        except:
            self.rmb.AppendText('没有该终点，请重新确认')
            return None

        '''根据计费标准计算计费'''
        if distance / 1000 < 6:
            needRmd = 3
        elif 6 < distance / 1000 < 12:
            needRmd = 4
        elif 12 < distance / 1000 < 22:
            needRmd = 5
        elif 22 < distance / 1000 < 32:
            needRmd = 6
        if distance / 1000 > 32:
            needRmd = 7 + (distance / 1000 - 32) // 20
        self.rmb.AppendText(str(needRmd) + '元  距离为' + str(distance) + '米')

if __name__ == '__main__':
    app = wx.App()
    MyFrame('北京地铁计费器')
    app.MainLoop()