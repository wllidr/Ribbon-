'''
    Desc:
        获取peer参数
'''
import re
import xlwt
import os
import easygui

def main(path):
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('Sheet1')
    style = xlwt.XFStyle() # 初始化样式
    font = xlwt.Font() # 为样式创建字体
    font.name = 'Times New Roman'
    font.bold = True # 黑体
    font.underline = True # 下划线
    font.italic = True # 斜体字
    style.font = font # 设定样式
    worksheet.col(0).width = 0x0d00 + 50 * 50
    for i in range(1, 10):
        worksheet.col(i).width = 0x0d00
    worksheet.write(0, 0, '<SYSNAME>')
    worksheet.write(0, 1, '<文件IP名称>')
    worksheet.write(0, 2, '<A对端>')
    worksheet.write(0, 3, '<A本端>')
    worksheet.write(0, 4, '<B对端>')
    worksheet.write(0, 5, '<B本端>')
    worksheet.write(0, 6, '<C对端>')
    worksheet.write(0, 7, '<C本端>')
    worksheet.write(0, 8, '<D对端>')
    worksheet.write(0, 9, '<D本端>')

    i = 1
    # print(path)
    files = os.listdir(path)
    files = sorted(files, key=lambda file:(int(file.split('--')[0].split('.')[-1]) + 1000 * int(file.split('--')[0].split('.')[-2])))

    for file in files:
        print('提取' + file + '文件中peer参数.......')
        device = ad = ab = bd = bb = cd = cb = dd = db = ''
        file = os.path.join(path, file)
        with open(file, 'rb') as f:
            string = ''
            for line in f:
                string += line.decode('utf8').strip() + '\n'

                if re.findall('sysname (.*?)', string):
                    device = re.search('sysname (.*?)\n', string).groups()[0]
                if re.findall('interface 40GE1/0/1\n', string):
                    try:
                        ad = re.findall('description To_.*?_(.*?)_.*?\n', string)[0]
                        ab = re.findall('ip address (.*?) 255.*?\n', string)[0]
                        # print(ad, ab)
                    except:
                        pass
                if re.findall('interface 40GE1/0/2\n', string):
                    try:
                        bd = re.findall('description To_.*?_(.*?)_.*?\n', string)[0]
                        bb = re.findall('ip address (.*?) 255.*?\n', string)
                    except:
                        pass
                if re.findall('interface 40GE1/0/3\n', string):
                    try:
                        cd = re.findall('description To_.*?_(.*?)_.*?\n', string)[0]
                        cb = re.findall('ip address (.*?) 255.*?\n', string)[0]
                    except:
                        pass
                if re.findall('interface 40GE1/0/4\n', string):
                    try:
                        dd = re.findall('description To_.*?_(.*?)_.*?\n', string)[0]
                        db = re.findall('ip address (.*?) 255.*?\n', string)[0]
                        # print(dd, db)
                    except:
                        pass
                if line.decode('utf8').strip() == '#':
                    string = ''

        worksheet.write(i, 0, device)
        worksheet.write(i, 1, os.path.basename(file).split('--')[0])
        worksheet.write(i, 2, ad)
        worksheet.write(i, 3, ab)
        worksheet.write(i, 4, bd)
        worksheet.write(i, 5, bb)
        worksheet.write(i, 6, cd)
        worksheet.write(i, 7, cb)
        worksheet.write(i, 8, dd)
        worksheet.write(i, 9, db)
        i += 1
    workbook.save('自动生成文件文件夹' + '/' + 'peer.xls')

def begin_peer(path):
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    print('开始peer参数采集.........')
    main(path)
    print('peer参数采集完成.........')
    easygui.msgbox('peer参数采集完成')

if __name__ == '__main__':
    begin_peer(r'C:\Users\Ribbon\Desktop\工作\润迅\自动化小工具\自动化刷脚本\Logger\1A')