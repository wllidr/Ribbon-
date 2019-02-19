'''
    Date : 2019 - 01 -06
    Desc:
        接入文件输出
'''
import sys; sys.path.append('.')
import re
import openConfigFile

def dealAcs(acFiles, acportConnects, ipPlans, devices, swPortConnect, fwPortConnect):
    # for port in acportConnects:
    #     print(port)
    # len(acFiles)
    for i in range(len(acFiles)):
        acFile = acFiles[i]
        acportConnect = acportConnects[i]
        sysname = acFile['sysname']
        # print(sysname)
        stackNumber = '不堆叠'
        if '不堆叠' in str(devices[i]['stackNumber']):
            stackFlag = False
        else:
            stackFlag = True
            stackNumber = int(devices[i]['stackNumber'])
        if stackFlag and stackNumber > 3:
            stackInfo = stackConfig(stackNumber, sysname)
        file = acFile['acFile']
        manageIp = acFile['manageIp']
        portInfos = acPorts(acportConnect, manageIp, stackFlag, stackNumber, swPortConnect, fwPortConnect)
        # print(sysname, file, manageIp)
        with open(sysname + '.txt', 'w') as f1:
            with openConfigFile.OpenConfigFile().open(file, mode='r', pwd='Pingan123'.encode('utf-8')) as f:
                string = ''
                for line in f:
                    try:
                        line = line.decode('gbk')
                    except:
                        line = line.decode('utf8', 'ignore')
                    string += line
                    if line.strip() == '#':
                        if re.search('sysname[\s\S]*?\n', string):
                            string = re.sub('sysname[\s\S]*?\n', 'sysname ' + sysname + '\n', string)
                        if re.search('interfacevlanif4094', re.sub(' ', '', string.lower())):
                            string = re.sub('ip\s*address[\s\S]*?\n', 'ip address ' + manageIp + ' ' + str(ipPlans[5]['mark']) + '\n', string)
                        if re.search('unicast-server', string):
                            string = re.sub('ntp-service\s*unicast-server[\s\S]*?\n',
                                            'ntp-service unicast-server ' + ipPlans[5]['ipStart'] + '\n', string)
                        if re.search('route-static', string):
                            string = re.sub('ip\s*route-static\s*[\s\S]*?\n',
                                            'ip route-static  0.0.0.0 0.0.0.0 ' + ipPlans[5]['ipStart'] + ' description To-CoreSwitch-MGMT\n', string)
                        if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string) and not re.search('用户配置', string):
                            string = re.sub('//[\s\S]*?\n', '\n', string)
                        f1.write(re.sub('\r', '', string))
                        string = ''
                if string.strip() != '' and string.strip()[-1] != '#':
                    if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string) and not re.search('用户配置', string):
                        string = re.sub('//[\s\S]*?\n', '\n', string)
                    f1.write(re.sub('\r', '', string))

        with open(sysname + '.txt', 'r') as f:
            info = f.read()
            # print(info)
            info = re.sub('接口配置[\s\S]*?——————', '接口配置：\n\n#\n——————', info)
            if stackFlag and stackNumber > 3:
                info = re.sub('堆叠配置[\s\S]*?——————', '堆叠配置：\n\n#\n——————', info)

        with open(sysname + '.txt', 'w', encoding='utf8') as f:
            string = ''
            for line in info.split('\n'):
                string += line +'\n'
                if line.strip() == '#':
                    if re.search('接口配置', string):
                        string = portInfos
                    if re.search('堆叠配置', string) and stackFlag and stackNumber > 3:
                        string += stackInfo
                    f.write(re.sub('\r', '', string))
                    string = ''
            if string.strip() != '' and string.strip()[-1] == '#':
                f.write(re.sub('\r', '', string))

def acPorts(acportConnect, manageIp, stackFlag, stackNumber, swPortConnect, fwPortConnect):
    # print(acportConnect['sysname'])
    vlan2To6 = ''
    temp = []
    temp1 = ['无线(友商)', '无线(华为)', '直播/培训', '有线', '安防', '其他']
    upLineFlag = True
    downLineFlag = True
    for acport in acportConnect['acPortConnect']:
        if acport['2'] in temp1:
            if acport['2'] not in temp:
                temp.append(acport['2'])
                for i in range(len(temp1)):
                    if acport['2'] == temp1[0] or acport['2'] == temp1[1]:
                        vlan2To6 += ' ' + str(2) + ' '
                        break
                    elif acport['2'] == temp1[i]:
                        vlan2To6 += ' ' + str(i + 1) + ' '
                        break
                    else:
                        pass

    vlan2To6 = ' '.join([t for t in sorted(list(set(vlan2To6.split(' ')))) if t.strip()!=''])
    # print(vlan2To6)
    string = '接口配置：\n'
    string += '\n' + 'interface Vlanif4094\n' + ' description To-SW&AP-MGMT  \n'
    string += ' ip address ' + re.sub('/', ' ', manageIp) + '\n'
    string += '#\n'

    for i in range(len(acportConnect['acPortConnect'])):
        # print(acportConnect['acPortConnect'][i]['2'])
        if acportConnect['acPortConnect'][i]['2'] == '有线':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group PC\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ' description To-PC\n' + ' port link-type access\n' + ' port default vlan 4\n'
            string += ' stp edged-port enable\n' + '#\n'

        elif acportConnect['acPortConnect'][i]['2'] == '无线(友商)':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group OtherAP\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ''' description To-Other-AP
 port link-type trunk
 port trunk pvid vlan 4094
 loopback-detect enable
 undo port trunk allow-pass vlan 1
 port trunk allow-pass vlan 2 4094
#\n'''
        elif acportConnect['acPortConnect'][i]['2'] == '无线(华为)':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group HuaweiAP\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ''' description To-Huawei-AP
 port link-type trunk
 port trunk pvid vlan 4094
 loopback-detect enable
 undo port trunk allow-pass vlan 1
 port trunk allow-pass vlan 2 4094
#\n'''
        elif acportConnect['acPortConnect'][i]['2'] == '直播/培训':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group LiveTraining\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ''' description To-Live&Training
 port link-type access
 port default vlan 3
 stp edged-port enable
#\n'''
        elif acportConnect['acPortConnect'][i]['2'] == '安防':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group Secure\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ''' description To-Secure
 port link-type access
 port default vlan 5
 stp edged-port enable
#\n'''
        elif acportConnect['acPortConnect'][i]['2'] == '其他':
            if 'S2700' not in acportConnect['sysname'] and 'S3700' not in acportConnect['sysname']:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'interface range ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            else:
                if (acportConnect['acPortConnect'][i]['0'] == acportConnect['acPortConnect'][i]['1']) or (acportConnect['acPortConnect'][i]['0'] != '' and acportConnect['acPortConnect'][i]['1'] == ''):
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                else:
                    string += 'port-group Other\n' + ' group-member ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + ' to ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
            string += ''' description To-Other
 port link-type access
 port default vlan 6
 stp edged-port enable
#\n'''
        elif acportConnect['acPortConnect'][i]['2'] == '单线上联' or acportConnect['acPortConnect'][i]['2'] == '单线下联':
            string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
            string += ' description To-CoreSwitch-' + acportConnect['acPortConnect'][i]['3'].replace('(光)', '') + '\n'
            string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
            string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + '#\n'

        elif '上行' in acportConnect['acPortConnect'][i]['2'] :
            if upLineFlag:
                if not stackFlag:
                    temp = acportConnect['acPortConnect'][i]['2'][-2]
                    string += 'interface Eth-Trunk' + temp + '\n'
                    string += ' description To-CoreSwitch-' + acportConnect['acPortConnect'][i]['3'] + '\n'
                    string += ' trunkport ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '')  + '\n'
                    string += ' trunkport ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '')  + '\n'
                    string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                    string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + '#\n'
                else:
                    string += 'interface Eth-Trunk1\n'
                    string += ' description To-CoreSwitch-' + acportConnect['acPortConnect'][i]['3'] + '\n'
                    # print(acportConnect['sysname'])
                    if 'S2720' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/10\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    elif 'S2750' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/4\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    elif 'S5720' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/48\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    upLineFlag = False
            # print(acportConnect['acPortConnect'][i])
            if 'Gigabit' in acportConnect['acPortConnect'][i]['0']:
                portHat = 'Gi'
            else:
                portHat = 'Eth'
            # print(portHat)
            if int(acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]) > 2:
                string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                string += ' description To-CoreSwitch-01-'+ acportConnect['acPortConnect'][i]['3'] + '_From-AccessSwitch-0' + acportConnect['acPortConnect'][i]['0'].split('/')[0][-1] + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                string += '#\n'
                if acportConnect['acPortConnect'][i]['1'] != '':
                    string += 'interface ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-' + acportConnect['acPortConnect'][i]['3'] + '_From-AccessSwitch-01-' + portHat + acportConnect['acPortConnect'][i]['1'].split('t')[-1] + '\n'
                    string += '#\n'
            else:
                for swport in swPortConnect:
                    if swport['2'] == acportConnect['acPortConnect'][i]['3']:
                        g1 = swport['0']
                        g2 = swport['1']
                for fwport in fwPortConnect:
                    if fwport['2'] == acportConnect['acPortConnect'][i]['3']:
                        g1 = fwport['0']
                        g2 = fwport['1']

                if int(acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]) <= 1 :
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g1.split('t')[-1] + '_From-AccessSwitch-01' + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                    string += '#\n'
                else:
                    if acportConnect['acPortConnect'][i]['0'].split('/')[0][-1] == 0:
                        tempnumber = 1
                    else:
                        tempnumber = acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g2.split('t')[-1] + '_From-AccessSwitch-0' + str(tempnumber) + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                    string += '#\n'
                # print(string)
                # print(acportConnect['acPortConnect'][i])

                if acportConnect['acPortConnect'][i]['1'] != '':
                    string += 'interface ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g2.split('t')[-1] + '_From-AccessSwitch-02-' + portHat + acportConnect['acPortConnect'][i]['1'].split('t')[-1] + '\n'
                    string += '#\n'
                # print(string)

        elif '下行' in acportConnect['acPortConnect'][i]['2']:
            if downLineFlag:
                if not stackFlag:
                    temp = acportConnect['acPortConnect'][i]['2'][-2]
                    string += 'interface Eth-Trunk' + temp + '\n'
                    string += ' description To-CoreSwitch-' + acportConnect['acPortConnect'][i]['3'] + '\n'
                    string += ' trunkport ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '')  + '\n'
                    string += ' trunkport ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '')  + '\n'
                    string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                    string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + '#\n'
                else:
                    string += 'interface Eth-Trunk2\n'
                    string += ' description To-CoreSwitch-' + acportConnect['acPortConnect'][i]['3'] + '\n'
                    if 'S2720' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/10\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    elif 'S2750' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/4\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    elif 'S5720' in acportConnect['sysname']:
                        for ab in range(1, stackNumber+1):
                            string +=  ' trunkport GigabitEthernet' + str(ab) + '/0/48\n'
                        string += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
                        string += ' port trunk allow-pass vlan ' + vlan2To6 + ' 4094\n' + ' mad detect mode relay\n' + '#\n'
                    downLineFlag = False
            # print(acportConnect['acPortConnect'][i])
            if 'Gigabit' in acportConnect['acPortConnect'][i]['0']:
                portHat = 'Gi'
            else:
                portHat = 'Eth'
            # print(portHat)
            if int(acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]) > 2:
                string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                string += ' description To-CoreSwitch-01-'+ acportConnect['acPortConnect'][i]['3'] + '_From-AccessSwitch-0' + acportConnect['acPortConnect'][i]['0'].split('/')[0][-1] + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                string += '#\n'
                if acportConnect['acPortConnect'][i]['1'] != '':
                    string += 'interface ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-' + acportConnect['acPortConnect'][i]['3'] + '_From-AccessSwitch-01-' + portHat + acportConnect['acPortConnect'][i]['1'].split('t')[-1] + '\n'
                    string += '#\n'
            else:
                for swport in swPortConnect:
                    if swport['2'] == acportConnect['acPortConnect'][i]['3']:
                        g1 = swport['0']
                        g2 = swport['1']
                for fwport in fwPortConnect:
                    if fwport['2'] == acportConnect['acPortConnect'][i]['3']:
                        g1 = fwport['0']
                        g2 = fwport['1']

                if int(acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]) <= 1 :
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g1.split('t')[-1] + '_From-AccessSwitch-01' + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                    string += '#\n'
                else:
                    if acportConnect['acPortConnect'][i]['0'].split('/')[0][-1] == 0:
                        tempnumber = 1
                    else:
                        tempnumber = acportConnect['acPortConnect'][i]['0'].split('/')[0][-1]
                    string += 'interface ' + acportConnect['acPortConnect'][i]['0'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g2.split('t')[-1] + '_From-AccessSwitch-0' + str(tempnumber) + '-' + portHat + acportConnect['acPortConnect'][i]['0'].split('t')[-1] + '\n'
                    string += '#\n'
                # print(string)
                # print(acportConnect['acPortConnect'][i])

                if acportConnect['acPortConnect'][i]['1'] != '':
                    string += 'interface ' + acportConnect['acPortConnect'][i]['1'].replace('(光)', '') + '\n'
                    string += ' description To-CoreSwitch-01-Gi' + g2.split('t')[-1] + '_From-AccessSwitch-02-' + portHat + acportConnect['acPortConnect'][i]['1'].split('t')[-1] + '\n'
                    string += '#\n'
    # print(string)
    return string

def stackConfig(stackNumber, sysname):
    # print(sysname, stackNumber)
    stackInfo = ''
    levels = [230, 200, 150, 0]
    if 'S2720' in sysname:
        for i in range(1, stackNumber + 1):
            stackInfo += 'interface stack-port 0/1\n'
            stackInfo += ' port interface Gigabitethernet 0/0/11 enable\n' + ' y\n#\n'
            stackInfo += 'interface stack-port 0/2\n'
            stackInfo += ' port interface Gigabitethernet 0/0/12 enable\n' + ' y\n#\n'
            stackInfo += 'stack slot 0 renumber ' + str(i) + '\n' + ' y\n#\n'
            if levels[i-1] != 0:
                stackInfo += 'stack slot 0 priority ' + str(levels[i-1]) + '\n' + ' y\n#\n'
            stackInfo += '\n'
    elif 'S2750' in sysname:
        for i in range(1, stackNumber + 1):
            stackInfo += 'interface stack-port 0/1\n'
            stackInfo += ' port interface Gigabitethernet 0/0/1 enable\n' + ' y\n#\n'
            stackInfo += 'interface stack-port 0/2\n'
            stackInfo += ' port interface Gigabitethernet 0/0/2 enable\n' + ' y\n#\n'
            stackInfo += 'stack slot 0 renumber ' + str(i) + '\n' + ' y\n#\n'
            if levels[i-1] != 0:
                stackInfo += 'stack slot 0 priority ' + str(levels[i-1]) + '\n' + ' y\n#\n'
            stackInfo += '\n'
    elif 'S5720' in sysname:
        for i in range(1, stackNumber + 1):
            stackInfo += 'interface stack-port 0/1\n'
            stackInfo += ' port interface XGigabitethernet 0/0/3 enable\n' + ' y\n#\n'
            stackInfo += 'interface stack-port 0/2\n'
            stackInfo += ' port interface XGigabitethernet 0/0/4 enable\n' + ' y\n#\n'
            stackInfo += 'stack slot 0 renumber ' + str(i) + '\n' + ' y\n#\n'
            if levels[i-1] != 0:
                stackInfo += 'stack slot 0 priority ' + str(levels[i-1]) + '\n' + ' y\n#\n'
            stackInfo += '\n'
    # print(stackInfo)
    return stackInfo

if __name__ == '__main__':
    acFiles = [{'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01', 'acFile': r'C:\\Users\\Ribbon\\Desktop\\平安2\\PingAnNet\\全场景标准配置脚本V1.7.2\\Access-SW-2750EI-单机.txt', 'manageIp': '133.150.1.2/25'}, {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-02', 'acFile': r'C:\Users\Ribbon\Desktop\平安2\PingAnNet\全场景标准配置脚本V1.7.2\Access-SW-2720EI-堆叠.txt', 'manageIp': '133.150.1.3/25'}]
    acportConnects = [{'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01',
      'acPortConnect': [{'0': 'Ethernet0/0/14', '1': 'Ethernet0/0/13', '2': '有线', '3': ''},
                        {'0': 'Ethernet0/0/13', '1': 'Ethernet0/0/15', '2': '无线(友商)', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}]}, {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-02',
                                                                 'acPortConnect': [
                                                                     {'0': 'Ethernet0/0/18', '1': 'Ethernet0/0/21',
                                                                      '2': '直播/培训', '3': ''},
                                                                     {'0': 'Ethernet0/0/1', '1': 'Ethernet0/0/1',
                                                                      '2': '无线(华为)', '3': ''},
                                                                     {'0': 'Ethernet0/0/7', '1': 'Ethernet0/0/8', '2': '单线上联', '3': 'Eth-Trunk12'},
                                                                     {'0': 'GigabitEthernet1/0/4', '1': '', '2': '上行（Ethrunk）', '3': 'GigabitEthernet1/1/4'},
                                                                     {'0': 'GigabitEthernet2/0/4', '1': '', '2': '上行（Ethrunk）','3': 'GigabitEthernet3/2/4'},
                                                                     {'0': 'GigabitEthernet3/0/4', '1': '', '2': '上行（Ethrunk）', '3': 'GigabitEthernet2/3/4'}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-2F-03',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-2F-04',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-4F-01',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-4F-02',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-4F-03',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-4F-04',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-4F-05',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]},
     {'sysname': 'LIFE-SW-HN-ZZ-NYL-S2700-4F-06',
      'acPortConnect': [{'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''},
                        {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]}]
    ipPlans = [{'segment': '133.146.28.0', 'ipStart': '133.146.28.1', 'ipEnd': '133.146.31.254', 'mark': 22, 'vlan': 2,
                'use': 'WIFI'},
               {'segment': '133.148.4.0', 'ipStart': '133.148.4.1', 'ipEnd': '133.148.4.126', 'mark': 25, 'vlan': 3,
                'use': 'ZhiBo&PeiXun'},
               {'segment': '133.148.4.128', 'ipStart': '133.148.4.129', 'ipEnd': '133.148.4.254', 'mark': 25, 'vlan': 4,
                'use': 'PC'},
               {'segment': '133.149.4.0', 'ipStart': '133.149.4.1', 'ipEnd': '133.149.4.126', 'mark': 25, 'vlan': 5,
                'use': 'Security'},
               {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 6,
                'use': 'Other'},
               {'segment': '133.150.1.0', 'ipStart': '133.150.1.1', 'ipEnd': '133.150.1.126', 'mark': 25, 'vlan': 4094,
                'use': '接入交换机&AP管理'},
               {'segment': '133.151.0.128', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25,
                'vlan': 'CORE_TO_AR1', 'use': '设备互连'},
               {'segment': '133.151.0.136', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25,
                'vlan': 'CORE_TO_AR2', 'use': '设备互连'},
               {'segment': '133.151.0.144', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25,
                'vlan': 'CORE_TO_FW(WAN)', 'use': '设备互连'},
               {'segment': '133.151.0.152', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25,
                'vlan': 'CORE_TO_FW(LAN)', 'use': '设备互连'},
               {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 7,
                'use': 'Free-Wifi'},
               {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 8,
                'use': 'zzzz'}]
    devices = [{'deviceName': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01', 'deviceRole': '接入交换机', 'deviceClass': 'S2750-28TP-PWR-EI-AC', 'stackNumber': '不堆叠', 'topDevice': '核心交换机'}, {'deviceName': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-02', 'deviceRole': '接入交换机', 'deviceClass': 'S2750-28TP-PWR-EI-AC', 'stackNumber': 4, 'topDevice': '核心交换机'}]
    dealAcs(acFiles, acportConnects, ipPlans, devices)