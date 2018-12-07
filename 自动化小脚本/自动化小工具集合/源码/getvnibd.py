'''
    Desc:
        获取VNI BD IP
'''
import os
import threadpool
import re
import xlwt

bdVniIps = []
def get_info(file):
    with open(file, 'rb') as f:
        string = ''
        bdVni = []
        for line in f:
            line = line.decode('utf8', 'ignore')
            string += line
            if line.strip() == '#':
                if re.search('bridge-domain \d', string) and re.search('vxlan vni \d', string):
                    # print(string)
                    bdNumber = re.search('bridge-domain (\d*)', string).groups()[0]
                    vniNumber = re.search('vxlan vni (\d*)', string).groups()[0]
                    bdVni.append('_'.join([bdNumber, vniNumber]))
                if re.search('interfaceVbdif', re.sub(' ', '', string)):
                    # print(string)
                    try:
                        ip = re.search('ip address (\d*\.\d*\.\d*\.\d*)', string).groups()[0]
                        bd1 = re.search('interface Vbdif([\s\S]*?)\n', string).groups()[0].strip()
                        for bd in bdVni:
                            bd2 = bd.split('_')[0]
                            if bd1 == bd2:
                                bdVniIps.append('_'.join([bd, ip]))
                                break
                    except:
                        pass
                        # print(string)
                string = ''

def begin_vni_bd(path):
    print('提取VNI BD IP号开始..........')
    if not os.path.exists('自动生成文件文件夹'):
        os.mkdir('自动生成文件文件夹')
    files = os.listdir(path)
    files = [os.path.join(path, file) for file in files]
    # files = [files[15]]
    pool = threadpool.ThreadPool(100)
    requests = threadpool.makeRequests(get_info, files)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    print(len(bdVniIps))
    allInfo = list(set(bdVniIps))
    allInfo = sorted(allInfo, key=lambda file: (int(file.split('.')[-1]) + 1000 * int(file.split('.')[-2]) + 1000000 * int(file.split('.')[-3])))
    print(len(allInfo))

    # 设置居中
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直方向
    style = xlwt.XFStyle()  # Create the Pattern
    style.alignment = alignment
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet1')
    for i in range(0, 3):
        worksheet.col(i).width = 0x0d00 + 50 * 50
    worksheet.write(0, 0, 'BD', style)
    worksheet.write(0, 1, 'VNI', style)
    worksheet.write(0, 2, 'IP_Address', style)
    j = 1
    for info in allInfo:
        # print(info)
        worksheet.write(j, 0, info.split('_')[0], style)
        worksheet.write(j, 1, info.split('_')[1], style)
        worksheet.write(j, 2, info.split('_')[2], style)
        j += 1
    workbook.save('自动生成文件文件夹/VNIBDIP提取表格.xls')
    print('VNI BD IP号提取结束..........')

if __name__ == '__main__':
    path = r'C:\Users\Ribbon\Desktop\润迅\自动化小工具\自动化刷脚本\Logger\1A'
    begin_vni_bd(path)