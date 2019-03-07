'''
    Date : 2018 - 11 -20
    Author : Ribbon Huang
    Desc:
        SN号等固资信息抽取
'''
import xlwt
import os
import re
import easygui

def Sn(filePath):
    print('开始采集SN、IP、设备类型、License等相关信息......')
    j = 1
    # 设置居中
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
    alignment.vert = xlwt.Alignment.VERT_TOP  # 垂直方向

    # 设置背景色
    pattern = xlwt.Pattern()  # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = 17

    pattern3 = xlwt.Pattern()  # Create the Pattern
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern3.pattern_fore_colour = 18

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('My Sheet')

    style = xlwt.XFStyle()  # Create the Pattern
    style.pattern = pattern  # Add Pattern to Style
    style.alignment = alignment

    pattern3 = xlwt.Pattern()  # Create the Pattern
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern3.pattern_fore_colour = 18
    style3 = xlwt.XFStyle()  # Create the Pattern
    style3.pattern = pattern3  # Add Pattern to Style
    style3.alignment = alignment

    style1 = xlwt.XFStyle()
    style1.alignment = alignment

    # 第一行参数----------------------------------
    worksheet.write(0, 0, '序号', style)
    worksheet.write(0, 1, '设备名称', style)
    worksheet.write(0, 2, '管理IP地址', style3)
    worksheet.write(0, 3, 'Loopback0地址', style3)
    worksheet.write(0, 4, 'Loopback1地址', style3)
    worksheet.write(0, 5, '设备类型', style)
    worksheet.write(0, 6, '版本信息', style3)
    worksheet.write(0, 7, '补丁信息', style3)
    worksheet.write(0, 8, 'License文件名', style3)
    worksheet.write(0, 9, 'License状态', style3)
    worksheet.write(0, 10, '机框SN信息', style)
    worksheet.write(0, 11, '板卡SN信息', style)
    worksheet.write(0, 12, '电源SN信息', style)
    worksheet.write(0, 13, '电源状态', style)
    worksheet.write(0, 14, '风扇SN信息', style)
    worksheet.write(0, 15, '风扇状态', style)
    worksheet.write(0, 16, '光模板SN信息', style)

    # 设置单元格长度
    for i in range(17):
        if i == 1 or i == 6 or i >= 10:
            worksheet.col(i).width = 0x0d00 + 100 * 50
        elif i == 0:
            worksheet.col(i).width = 0x0a00
        else:
            worksheet.col(i).width = 0x0d00 + 100 * 20

    BKSNIF, DYSNIF, FSSNIF, GMKSNIF = [True, True, True, True]
    files = os.listdir(filePath)
    files = [os.path.join(filePath, file) for file in files]

    flag = interfFlag = versionFlag = patchFlag = licenseFlag = False
    for file in files:
        deviceInfo = ''
        snAllInfo = []
        loopback0 = loopback1 = manageIp = version = deviceType = patch = license = licensestate = deviceName = jksn = ''
        time = 0
        with open(file, 'rb') as f:
            temp = re.search('device\s*status([\s\S]*?)<', f.read().decode('utf8', 'ignore').lower())
            try:
                deviceInfo = temp.groups()[0]
            except:
                pass

        with open(file, 'rb') as f:
            for line in f:
                if re.search('<[\s\S]*?>', line.decode('utf8', 'ignore')):
                    if time == 0:
                        deviceName = re.search('<([\s\S]*?)>', line.decode('utf8', 'ignore')).groups()[0]
                        time += 1
                    flag = interfFlag = versionFlag = patchFlag = licenseFlag = False
                if flag:
                    if 'Equipment SN(ESN)' in line.decode('utf8', 'ignore'):
                        jksn = line.decode('utf8', 'ignore').split(':')[-1].strip()
                        continue
                    snAllInfo.append(line.decode('utf8', 'ignore'))
                if 'dissnall' in re.sub(' ', '', line.decode('utf8', 'ignore')) or 'displaysnall' in re.sub(' ', '',line.decode('utf8','ignore')):
                    flag = True

                if 'disipinterfacebrief' in re.sub(' ', '', line.decode('utf8',
                                                                        'ignore')) or 'displayipinterfacebrief' in re.sub(
                        ' ', '', line.decode('utf8', 'ignore')):
                    interfFlag = True

                if 'disversion' in re.sub(' ', '', line.decode('utf8', 'ignore')) or 'displayversion' in re.sub(' ', '',line.decode('utf8','ignore')):
                    versionFlag = True

                if 'dispatch-information' in re.sub(' ', '', line.decode('utf8',
                                                                         'ignore')) or 'displaypatch-information' in re.sub(
                        ' ', '', line.decode('utf8', 'ignore')):
                    patchFlag = True

                if 'displaylicense' in re.sub(' ', '', line.decode('utf8', 'ignore')) or 'dislicense' in re.sub(' ', '',line.decode('utf8','ignore')):
                    licenseFlag = True

                if interfFlag:
                    line = line.decode('utf8', 'ignore')
                    if re.search('LoopBack0', line):
                        loopback0 = [i for i in line.split(' ') if re.search('\S', i)][1]
                    if re.search('LoopBack1', line):
                        loopback1 = [i for i in line.split(' ') if re.search('\S', i)][1]
                    if re.search('meth0/0/0', line.lower()):
                        manageIp = [i for i in line.split(' ') if re.search('\S', i)][1]

                if versionFlag:
                    line = line.decode('utf8', 'ignore')
                    if re.search('VRP.*?software,', line):
                        version = [i for i in line.split('(') if re.search('\S', i)][-1]
                        version = version.split(')')[0]
                        version = version.strip().split(' ')[-1]

                    if re.search('HUAWEI(.*?)uptime is ', line):
                        deviceType = re.search('HUAWEI(.*?)uptime is ', line).groups()[0]

                if patchFlag:
                    line = line.decode('utf8', 'ignore')
                    if re.search('PatchPackageVersion', re.sub(' ', '', line)):
                        patch = line.split(':')[-1].strip()

                if licenseFlag:
                    line = line.decode('utf8', 'ignore')
                    if re.search('Active License', line) and re.search(':/', line):
                        license = line.split(':/')[-1].strip()
                    if re.search('License state', line):
                        licensestate = line.split(':')[-1].strip().split('.')[0]

        if loopback0 != '':
            worksheet.write(j, 3, loopback0, style1)
        else:
            worksheet.write(j, 3, '--', style1)
        if loopback1 != '':
            worksheet.write(j, 4, loopback1, style1)
        else:
            worksheet.write(j, 4, '--', style1)
        if manageIp != '':
            worksheet.write(j, 2, manageIp, style1)
        else:
            worksheet.write(j, 2, '--', style1)
        if version != '':
            worksheet.write(j, 6, version, style1)
        else:
            worksheet.write(j, 6, '--', style1)
        if patch != '':
            worksheet.write(j, 7, patch, style1)
        else:
            worksheet.write(j, 7, '--', style1)
        if license != '':
            worksheet.write(j, 8, license, style1)
        else:
            worksheet.write(j, 8, '--', style1)
        if licensestate != '':
            worksheet.write(j, 9, licensestate, style1)
        else:
            worksheet.write(j, 9, '--', style1)
        worksheet.write(j, 0, j, style1)
        if deviceName != '':
            worksheet.write(j, 1, deviceName, style1)
        else:
            worksheet.write(j, 1, '--', style1)
        if deviceType != '':
            worksheet.write(j, 5, deviceType, style1)
        else:
            worksheet.write(j, 5, '--', style1)
        if jksn != '':
            worksheet.write(j, 10, jksn, style1)
        else:
            worksheet.write(j, 10, '--', style1)

        if BKSNIF:
            bksn = []
            for info in snAllInfo:
                if jksn not in info and not re.search('PWR', info) and not re.search('FAN', info) and not re.search(
                        '\dGE\d/\d/\d', info):
                    break
                elif re.search('^\d[\S\s]*?--[\S\s]*?\n', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    if info[-2] != '--' and info[-2] not in bksn:
                        bksn.append(info[-2])
            if bksn:
                worksheet.write(j, 11, ';'.join(bksn), style1)
            else:
                worksheet.write(j, 11, '--', style1)
        else:
            worksheet.write(j, 11, '--', style1)

        if DYSNIF:
            dysn = []
            for info in snAllInfo:
                if re.search('PWR\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    if info[2] not in dysn:
                        dysn.append(info[-2])
            if dysn:
                worksheet.write(j, 12, ';'.join(dysn), style1)
            else:
                worksheet.write(j, 12, '--', style1)
            dystatus = []
            for infotemp in deviceInfo.split('\n'):
                if re.search('pwr\d', infotemp.lower()):
                    if re.search('pwr\d[\s\S]*?present[\s\S]*?on\s*registered\s*normal', infotemp.lower()):
                        dystatus.append('normal')
                    else:
                        dystatus.append('error')
            if dystatus:
                worksheet.write(j, 13, ';'.join(dystatus), style1)
            else:
                worksheet.write(j, 13, '--', style1)
        else:
            worksheet.write(j, 12, '--', style1)
            worksheet.write(j, 13, '--', style1)

        if FSSNIF:
            fssn = []
            for info in snAllInfo:
                if re.search('FAN\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    if info[2] not in fssn:
                        fssn.append(info[-2])
            if fssn:
                worksheet.write(j, 14, ';'.join(fssn), style1)
            else:
                worksheet.write(j, 14, '--', style1)
            fsstatus = []
            for infotemp in deviceInfo.split('\n'):
                if re.search('fan\d', infotemp.lower()):
                    if re.search('fan\d[\s\S]*?present[\s\S]*?on\s*registered\s*normal', infotemp.lower()):
                        fsstatus.append('normal')
                    else:
                        fsstatus.append('error')
            if fsstatus:
                worksheet.write(j, 15, ';'.join(fsstatus), style1)
            else:
                worksheet.write(j, 15, '--', style1)
        else:
            worksheet.write(j, 14, '--', style1)
            worksheet.write(j, 15, '--', style1)

        if GMKSNIF:
            gmksn = []
            for info in snAllInfo:
                if re.search('\dGE\d/\d/\d', info):
                    info = [i for i in info.split(' ') if re.search('\S', i)]
                    if info[2] != '--':
                        if info[2] not in gmksn:
                            gmksn.append(info[2])
            if gmksn:
                worksheet.write(j, 16, ';'.join(gmksn), style1)
            else:
                worksheet.write(j, 16, '--', style1)
        else:
            worksheet.write(j, 16, '--', style1)
        # print('\r完成进度: %3.2f%%' %((j - 1) / len(files) * 100), end='')
        j += 1


    # print('\r完成进度: %3.2f%%' %(100), end='')
    workbook.save('采集SN信息.xls')
    easygui.msgbox('提取SN作业完成')