'''
    Date : 2019 - 1 - 4
    Author: Ribbon Huang
    Desc:
        这里主要是为了获取表中的参数，存储在变量中
        其中根据网段掩码计算 网段开始到网段结束
        获取职场类型 以及 获取 设备的相关参数
'''
import sys; sys.path.append('.')
import pandas as pd
import os
import ipCacl

ipPlans = []  # {'segment':'网段', 'ipStart':'网段开始', 'ipEnd':'网段结束', 'mark':'掩码',
                # 'vlan':'VLAN', 'use':'用途'}
bussniessClass = ''
devices = []  # {'deviceName':'设备名称', 'deviceRole':'设备角色', 'deviceClass':'设备类型',
                # 'stackNumber' : '堆叠数量', 'topDevice':'上联设备'}

def InitialVariables():
    fwYN = '无FW'
    swModel = ''
    # print(os.listdir(os.path.dirname(os.path.dirname(__file__))))
    file = [file for file in os.listdir('.') if
              'xls' in file.lower() and '工具源标准数据' in file.lower() and not '~' in file]
    # print(file)
    file = file[0]
    file = os.path.join(os.path.dirname('.'), file)
    ipDf = pd.read_excel(file, sheet_name='IP规划', header=None).dropna(axis=0, how='all').fillna(0)
    for i in range(2, ipDf.shape[0]):
        temp = ipDf.iloc[i, ].tolist()
        # print(temp)
        ipStart,ipEnd = ipCacl.ipBegin(temp[0].strip() + '/' + str(int(temp[1])), int(temp[-2]), int(temp[-1]))
        ipPlans.append({'segment':temp[0], 'ipStart': ipStart, 'ipEnd':ipEnd, 'mark':temp[1],
                       'vlan':temp[2], 'use':temp[3]})
    # for ipPlan in ipPlans:
    #     print(ipPlan)

    df = pd.read_excel(file, sheet_name='设备', header=None).dropna(axis=0, how='all')
    for i in range(df.shape[0]):
        if '网络设备命名标准规范' in df.iloc[i, 0]:
            break

    num = i
    bussniessClass = df.iloc[1, ].tolist()[0]
    for j in range(3, num):
        temp = df.iloc[j, ].tolist()
        devices.append({'deviceName': temp[0], 'deviceRole': temp[1], 'deviceClass': temp[2],
                        'stackNumber' : temp[3], 'topDevice': temp[4]})
        if 'S5720HI' in temp[0].upper() and '核心' in temp[1] :
            swModel = 'S5720HI'
        elif 'S5720EI' in temp[0] and '核心' in temp[1] :
            swModel = 'S5720EI'
        if 'FW' in temp[0].upper():
            fwYN = '有FW'
    # print([device for device in devices if '接入' in device['deviceRole']])
    return ipPlans, bussniessClass.upper(), devices, swModel.upper(), fwYN.upper()

if __name__ == '__main__':
    print(InitialVariables())
