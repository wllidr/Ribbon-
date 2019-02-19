'''
    Author: Ribbon Huang
    Date: 2019 - 1 - 5
    Desc:
        模板的选择， 以及sysname的绑定
'''
import sys; sys.path.append('.')
import os
import easygui
import zipfile

def fileSelect(bussniessClass, fwYN, devices, swModel, ipPlans):
    path = [file for file in os.listdir('.') if '全场景标准配置脚本' in file][0]
    zf = zipfile.ZipFile(path)
    files = [file.encode('cp437').decode('gbk') for file in zf.namelist()]
    # print(files)

    # # 防火墙文件选择
    temp = ''
    for device in devices:
        if '防火墙' in device['deviceRole']:
            temp = device['deviceName']
    if (bussniessClass[0]== 'D' or bussniessClass[0] == 'E') and fwYN == '有FW':
        fwFile = [file for file in files if bussniessClass[0] in file and '类' in file ]
        if bussniessClass[0]== 'D' :
            fwFile = [file for file in fwFile if '核心' in file][0]
        fwFile = {'sysname': temp, 'fwFile': fwFile}
    elif (bussniessClass[0]== 'A' or bussniessClass[0] == 'B' or bussniessClass[0] == 'C') and fwYN == '有FW':
        fwFile = [file for file in files if bussniessClass[0] in file and '类' in file][0]
        fwFile = {'sysname': temp, 'fwFile': fwFile.encode('gbk').decode('cp437')}
    else:
        fwFile = ''
    # print(fwFile)

    # 核心文件选择
    temp = ''
    for device in devices:
        if '核心' in device['deviceRole'] :
            temp = device['deviceName']
    if bussniessClass[0] == 'A' or bussniessClass[0] == 'B' or bussniessClass[0] == 'C':
        swFile = [file for file in files if fwYN in file and swModel in file][0]
        swFile = {'sysname':temp, 'swFile': swFile.encode('gbk').decode('cp437')}
    else:
        swFile = ''
    # print(swFile)

    # 接入文件的选择，以及接入交换机 sysname
    for ipPlan in ipPlans:
        if str(ipPlan['vlan']).strip() == '4094':
            manageIp = ipPlan['ipStart'].strip()
            mark = str(ipPlan['mark'])
            reservedNumber = int(ipPlan['reservedNumber'])
    acFiles = []
    temps = [file for file in files if 'access' in file.lower()]
    i = 1
    for device in devices:
        # print(device)
        if '接入' in device['deviceRole'] :
            if str(device['stackNumber']) != '不堆叠':
                try:
                    acFile = [temp for temp in temps if device['deviceClass'][1:5] in temp and '堆叠' in temp][0]
                except:
                    easygui.msgbox('选择型号错误或者是堆叠台数类型有误')
            else:
                # print(temps)
                # print(device['deviceClass'])
                try:
                    acFile = [temp for temp in temps if device['deviceClass'][1:5] in temp and '单机' in temp][0]
                except:
                    easygui.msgbox('选择型号错误或者是堆叠台数类型有误')

            if bussniessClass[0]== 'D' and fwYN == '无FW':
                manageIp1 = '.'.join(manageIp.split('.')[:-1]) + '.' + str((int(manageIp.split('.')[-1]) + i + 3))
            else:
                manageIp1 = '.'.join(manageIp.split('.')[:-1]) + '.' + str((int(manageIp.split('.')[-1]) + i))
            i += 1
            acFiles.append({'sysname':device['deviceName'], 'acFile': acFile.encode('gbk').decode('cp437'), 'manageIp':manageIp1 + '/' + str(int(mark)), 'stackNumber' : device['stackNumber']})
    # print(acFiles)
    return acFiles, swFile, fwFile

if __name__ == '__main__':
    devices = [{'deviceName': 'LIFE-SW-HN-ZZ-NYL-S2700-2F-04', 'deviceRole': '核心交换机', 'deviceClass': 'S2700-26TP-EI-AC', 'stackNumber': '不堆叠', 'topDevice': '核心交换机'},
               {'deviceName': 'LIFE-SW-HN-ZZ-NYL-S2700-2F-05', 'deviceRole': '接入交换机', 'deviceClass': 'S3700-52P-EI-AC-PWR', 'stackNumber': '不堆叠', 'topDevice': '核心交换机'},
               {'deviceName': 'LIFE-SW-HN-ZZ-NYL-S2700-2F-05', 'deviceRole': '防火墙', 'deviceClass': 'S2750-26TP-EI-AC','stackNumber': '堆叠', 'topDevice': '核心交换机'}]
    swModel = '5720HI'
    ipPlans = [{'segment': '133.146.28.0', 'ipStart': '133.146.28.1', 'ipEnd': '133.146.31.254', 'mark': 22, 'vlan': 2, 'use': 'WIFI', 'reservedNumber':0}, {'segment': '133.148.4.0', 'ipStart': '133.148.4.1', 'ipEnd': '133.148.4.126', 'mark': 25, 'vlan': 3, 'use': 'ZhiBo&PeiXun', 'reservedNumber':0},
               {'segment': '133.148.4.128', 'ipStart': '133.148.4.129', 'ipEnd': '133.148.4.254', 'mark': 25, 'vlan': 4, 'use': 'PC', 'reservedNumber':0}, {'segment': '133.149.4.0', 'ipStart': '133.149.4.1', 'ipEnd': '133.149.4.126', 'mark': 25, 'vlan': 5, 'use': 'Security', 'reservedNumber':0},
               {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 6, 'use': 'Other', 'reservedNumber':0}, {'segment': '133.150.1.0', 'ipStart': '133.150.1.1', 'ipEnd': '133.150.1.126', 'mark': 25, 'vlan': 4094, 'use': '接入交换机&AP管理', 'reservedNumber':0},
               {'segment': '133.151.0.128', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25, 'vlan': 'CORE_TO_AR1', 'use': '设备互连', 'reservedNumber':0}, {'segment': '133.151.0.136', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.158', 'mark': 27, 'vlan': 'CORE_TO_AR2', 'use': '设备互连', 'reservedNumber':0}, ]
    fileSelect('A类', '有FW', devices, swModel, ipPlans)
    # for i in fileSelect('A类', '有FW', devices, swModel, ipPlans):
    #     print(i)