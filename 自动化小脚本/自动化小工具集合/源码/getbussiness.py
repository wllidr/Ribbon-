import xlrd
import xlwt
import os
import pandas as pd

def create_Excel(fileName):
    '''生成下发业务总表'''
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    if not os.path.exists('自动生成文件文件夹/业务下发'):
        os.mkdir('自动生成文件文件夹/业务下发')
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('Sheet1')
    # 设置居中
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
    style = xlwt.XFStyle()  # Create the Pattern
    style.alignment = alignment
    worksheet.write(0, 0, '逻辑交换机名称', style)
    worksheet.write(0, 1, '逻辑端口名称', style)
    worksheet.write(0, 2, '设备名称', style)
    worksheet.write(0, 3, '端口名称', style)
    worksheet.write(0, 4, '接入方式', style)
    worksheet.write(0, 5, 'vlanId', style)
    worksheet.write(0, 6, '设备组类型', style)
    worksheet.write(0, 7, '描述', style)
    for ppp in range(0, 2):
        worksheet.col(ppp).width = 0x0d00 + 50 * 20
    worksheet.col(2).width = 0x0d00 + 50* 50
    worksheet.col(7).width = 0x0d00 + 50 * 50
    for ppp in range(3, 7):
        worksheet.col(ppp).width = 0x0d00 + 50 * 20

    j = 1
    workBook = xlrd.open_workbook(fileName)
    try:
        business = workBook.sheet_by_name('业务下发')
    except:
        business = workBook.sheet_by_name('Sheet1')
    nrows = business.nrows
    devices = []
    for i in range(1, nrows):
        try:
            value = business.row_values(i)
            if value[0].strip() != '':
                devices = value[0].strip().split('\n')
            ip = value[1].strip()
            if value[2] != '':
                vlanId = str(int(value[2]))
            else:
                vlanId = ''
            # print(ip, vlanId)
            portClass = value[3].strip()
            portStart = int(value[4].strip().split('-')[0])
            portEnd = int(value[4].strip().split('-')[-1])
            joinClass = value[5].strip()
            # print(portClass)
            # print(portStart, portEnd)
            for device in devices:
                for g in range(portStart, portEnd + 1):
                    worksheet.write(j, 0, ip, style)
                    if vlanId.strip() != '':
                        worksheet.write(j, 1, device[2:7] + '_' + vlanId + '_' + str(g), style)
                    else:
                        worksheet.write(j, 1, device[2:7] + '_' + joinClass + '_' + str(g), style)
                    worksheet.write(j, 2, device, style)
                    worksheet.write(j, 3, portClass + str(g), style)
                    worksheet.write(j, 4,  joinClass, style)
                    worksheet.write(j, 5,  vlanId, style)
                    worksheet.write(j, 6, '单设备', style)
                    if joinClass.lower() == 'dot1q':
                        worksheet.write(j, 7, 'Port_' + ip + '_' + vlanId, style)
                    else:
                        worksheet.write(j, 7, 'Port_' + ip, style)
                    j += 1
        except:
            print(business.row_values(i))
    workbook.save('自动生成文件文件夹/业务下发/业务下发总表.xls')

def split_table():
    df = pd.read_excel('自动生成文件文件夹/业务下发/业务下发总表.xls', sheet_name='Sheet1')
    i = 1
    while True:
        if 468 * i - 1 < df.shape[0]:
            d = df.ix[468 * (i - 1) : 468 * i - 1, :]
            d.to_excel('自动生成文件文件夹/业务下发/业务下表分表' + str(i) + '.xls', index=None)
            i += 1
        else:
            d = df.ix[468 * (i - 1): df.shape[0], :]
            d.to_excel('自动生成文件文件夹/业务下发/业务下表分表' + str(i) + '.xls', index=None)
            break

def begin_bussiness(filePath):
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    print('开始生成业务下发表..................')
    create_Excel(filePath)
    split_table()
    print('业务下发表生成完毕..................')

if __name__ == '__main__':
    filePath = r'D:\shengkai\3.6\集成应用\工具表格模板.xls'
    begin_bussiness(filePath)

