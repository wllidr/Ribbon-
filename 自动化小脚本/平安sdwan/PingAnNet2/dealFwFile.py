'''
    Date : 2019 - 01 -06
    Desc:
        防火墙文件输出, 总共分成三类处理， ABC一类处理， D一类处理， E一类处理
'''
import sys; sys.path.append('.')
import re

wildcardMark = {'1': '127.255.255.255', '2': '63.255.255.255', '3': '31.255.255.255', '4': '15.255.255.255',
                '5': '7.255.255.255', '6': '3.255.255.255', '7': '1.255.255.255', '8': '0.255.255.255',
                '9': '0.127.255.255', '10': '0.63.255.255', '11': '0.31.255.255', '12': '0.15.255.255',
                '13': '0.7.255.255', '14': '0.3.255.255', '15': '0.1.255.255', '16': '0.0.255.255',
                '17': '0.0.127.255', '18': '0.0.63.255', '19': '0.0.31.255', '20': '0.0.15.255',
                '21': '0.0.7.255', '22': '0.0.3.255', '23': '0.0.1.255', '24': '0.0.0.255',
                '25': '0.0.0.127', '26': '0.0.0.63', '27': '0.0.0.31', '28': '0.0.0.15', '29': '0.0.0.7',
                '30': '0.0.0.3', '31': '0.0.0.1', '32': '0.0.0.0'}

def dealABC(fwFile, ipPlans):
    ips = []
    for ipPlan in ipPlans:
        ipPlan['vlan'] = str(ipPlan['vlan'])
        if ipPlan['vlan'].upper().strip() == 'CORE_TO_AR1':
            ips.append('.'.join(ipPlan['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(int(ipPlan['ipStart'].split('-')[0].split('.')[-1].strip()) + 1))
        if ipPlan['vlan'].upper().strip() == 'CORE_TO_AR2':
            ips.append('.'.join(ipPlan['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(int(ipPlan['ipStart'].split('-')[0].split('.')[-1].strip()) + 1))
        if str(ipPlan['vlan']).strip() == '7' or str(ipPlan['vlan']).strip() == '8':
            Flag78 = True

    sysname = fwFile['sysname']
    file = fwFile['fwFile']
    with open(sysname + '.txt', 'w') as f:
        string = ''
        with open(file, 'rb') as f1:
            for line in f1:
                line = line.decode('gbk', 'ignore')
                string += line
                if line.strip() == '#':
                    if re.search('sysname[\s\S]*?', string):
                        string = re.sub('sysname[\s\S]*?\n', 'sysname ' + sysname + '\n', string)
                    if re.search('unicast-server', string):
                        ntps = re.findall('unicast-server[\s\S]*?\n', string)
                        for i in range(len(ips)):
                            string = re.sub(ntps[i], 'unicast-server ' + ips[i] + '\n', string)
                    if re.search('interfaceeth-trunk1', re.sub(' ', '', string.lower())):
                        string = re.sub('ip\s*address[\s\S]*?\n', 'ip address ' + '.'.join(
                            ipPlans[8]['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                            int(ipPlans[8]['ipStart'].split('-')[0].split('.')[-1].strip()) + 1) + ' ' + str(
                            int(ipPlans[8]['mark'])) + '\n', string)
                    if re.search('interfaceeth-trunk2', re.sub(' ', '', string.lower())):
                        string = re.sub('ip\s*address[\s\S]*?\n', 'ip address ' + '.'.join(
                            ipPlans[9]['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                            int(ipPlans[9]['ipStart'].split('-')[0].split('.')[-1].strip()) + 1) + ' ' + str(
                            int(ipPlans[9]['mark'])) + '\n', string)
                    if re.search('network', string):
                        string = re.sub('network[\s\S]*?\n', 'network ' + ipPlans[8]['segment'] + '  ' + wildcardMark[
                            str(int(ipPlans[8]['mark']))] + '\n', string)
                    if re.search('route-static', string):
                        routes = re.findall('route-static[\S\s]*?\n', string)
                        descriptions = [' description Wife  \n', ' description Live&Training\n', ' description Pc \n',
                                        ' description Secure \n', ' description Other  \n',
                                        ' description SW&AP-Manage \n']
                        for i in range(len(routes)):
                            string = re.sub(routes[i], 'route-static ' + ipPlans[i]['ipStart'].split('-')[0] + ' ' + str(
                                int(ipPlans[i]['mark'])) + ' ' + '.'.join(
                                ipPlans[9]['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                                int(ipPlans[9]['ipStart'].split('-')[0].split('.')[-1].strip()) + 1) + descriptions[i], string)
                    if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string):
                        string = re.sub('//[\s\S]*?\n', '\n', string)
                    f.write(re.sub('\r', '', string))
                    string = ''
        if string.strip() != '' and string.strip()[-1] != '#':
            if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string):
                string = re.sub('//[\s\S]*?\n', '\n', string)
            f.write(re.sub('\r', '', string))

def dealDE(fwFile, ipPlans, fwportConnect, dns1, dns2, option):
    ips = []
    Flag78 = False
    vlan78Info = ''
    for ipPlan in ipPlans:
        ipPlan['vlan'] = str(ipPlan['vlan'])
        if ipPlan['vlan'].upper().strip() == 'CORE_TO_AR1':
            ips.append('.'.join(ipPlan['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                int(ipPlan['ipStart'].split('-')[0].split('.')[-1].strip()) + 1))
        if ipPlan['vlan'].upper().strip() == 'CORE_TO_AR2':
            ips.append('.'.join(ipPlan['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                int(ipPlan['ipStart'].split('-')[0].split('.')[-1].strip()) + 1))
        if str(ipPlan['vlan']).strip() == '7' or str(ipPlan['vlan']).strip() == '8':
            Flag78 = True
    # for ipPlan in ipPlans:
    #     print(ipPlan)
    fwPortInfos = ''
    firewall = 'firewall zone trust   \n'
    firewall += ' add interface vlanif2\n' + ' add interface vlanif3\n' + ' add interface vlanif4\n'
    firewall += ' add interface vlanif5\n' + ' add interface vlanif6\n' + ' add interface vlanif4094\n'
    for fwPort in fwportConnect:
        if fwPort['0'] != '' and fwPort['1']!='' and fwPort['2']!='':
            firewall += ' add interface  ' + fwPort['2'] + '\n'
            fwPortInfos += 'interface ' + fwPort['2'] + '\n'
            fwPortInfos += ' description To-LAN-AccessSwitch-Eth_Trunk1'  + '\n'
            fwPortInfos += ''' portswitch
 service-manage ping permit
 service-manage ssh permit
 service-manage snmp permit\n'''
            if fwPort['mad'] != '':
                fwPortInfos += ' mad relay\n'
            fwPortInfos += '#\n'
            fwPortInfos += 'interface ' + fwPort['0'] + '\n'
            fwPortInfos += ' description To-AccessSwitch-' + '-'.join(fwPort['3']['sysname'].split('-')[-3:]) + '-Gi' + fwPort['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + fwPort['0'].split('t')[-1] + '\n'
            # fwPortInfos += ' description To-AccessSwitch-01-Gi0/0/X_From-FW-01-Gi' + fwPort['0'].split('t')[-1] + '\n'
            fwPortInfos += ' portswitch\n'
            fwPortInfos += ' eth-trunk ' + fwPort['2'].split('k')[-1] + '\n#\n'
            fwPortInfos += 'interface ' + fwPort['1'] + '\n'
            fwPortInfos += ' description To-AccessSwitch-' + '-'.join(fwPort['3']['sysname'].split('-')[-3:]) + '-Gi' + fwPort['3']['1'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + fwPort['1'].split('t')[-1] + '\n'
            fwPortInfos += ' portswitch\n'
            fwPortInfos += ' eth-trunk ' + fwPort['2'].split('k')[-1] + '\n#\n'
        elif fwPort['0'] != '' and fwPort['1'] == '' and fwPort['2'] == '':
            firewall += ' add interface  ' + fwPort['0'] + '\n'
            fwPortInfos += 'interface ' + fwPort['0'] + '\n'
            fwPortInfos += ' description To-AccessSwitch-' + '-'.join(fwPort['3']['sysname'].split('-')[-3:]) + '-Gi' + fwPort['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + fwPort['0'].split('t')[-1] + '\n'
            fwPortInfos += ''' portswitch
 service-manage ping permit
 service-manage ssh permit
 service-manage snmp permit\n'''
            if fwPort['mad'] != '':
                fwPortInfos += ' mad relay\n'
            fwPortInfos += '#\n'
        elif fwPort['0'] == '' and fwPort['1'] != '' and fwPort['2'] == '':
            firewall += ' add interface  ' + fwPort['1'] + '\n'
            fwPortInfos += 'interface ' + fwPort['1'] + '\n'
            if fwPort['3']['0'] != '':
                fwPortInfos += ' description To-AccessSwitch-' + '-'.join(fwPort['3']['sysname'].split('-')[-3:]) + '-Gi' + fwPort['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + fwPort['1'].split('t')[-1] + '\n'
            else:
                fwPortInfos += ' description To-AccessSwitch-' + '-'.join(fwPort['3']['sysname'].split('-')[-3:]) + '-Gi' + fwPort['3']['1'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + fwPort['1'].split('t')[-1] + '\n'
            fwPortInfos += ''' portswitch
 service-manage ping permit
 service-manage ssh permit
 service-manage snmp permit\n'''
            if fwPort['mad'] != '':
                fwPortInfos += ' mad relay\n'
            fwPortInfos += '#\n'
    firewall += '#\n'
    # print(fwPortInfos)
    # print(firewall)
    DNS = dns1 + ' ' + dns2
    if Flag78:
        vlan78Info, other = vlan78(ipPlans, DNS)
    sysname = fwFile['sysname']
    file = fwFile['fwFile']
    # print(file)
    with open(sysname + '.txt', 'w') as f:
        string = ''
        with open(file, 'rb') as f1:
            for line in f1:
                line = line.decode('gbk', 'ignore')
                string += line
                if line.strip() == '#':
                    if re.search('dhcpserverdns-list', re.sub(' ', '', string.lower())):
                        string = re.sub('dns-list[\s\S]*?\n', 'dns-list  ' + DNS + '\n', string)
                    if re.search('sysname[\s\S]*?', string):
                        string = re.sub('sysname[\s\S]*?\n', 'sysname ' + sysname + '\n', string)
                    if re.search('unicast-server', string):
                        ntps = re.findall('unicast-server[\s\S]*?\n', string)
                        for i in range(len(ntps)):
                            string = re.sub(ntps[i], 'unicast-server ' + '.'.join(
                            ipPlans[8+i]['ipStart'].split('-')[0].split('.')[:-1]) + '.' + str(
                            int(ipPlans[8+i]['ipStart'].split('-')[0].split('.')[-1].strip()) + 1) + '\n', string)
                    if re.search('network', string):
                        networks = re.findall('network[\s\S]*?\n', string)
                        for i in range(len(networks)):
                            temp = ipPlans[6+i]['segment'] + ' ' + wildcardMark[str(int(ipPlans[6+i]['mark'] ))]
                            string = re.sub(networks[i], 'network ' + temp + '\n', string)
                    if re.search('interfacevlanif2', re.sub(' ', '', string.lower())):
                        # print (string)
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[0]['ipStart'] + ' ' + str(
                            int(ipPlans[0]['mark'])) + '\n', string)
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[0]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[0]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[0]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[0]['ipEnd'] + '\n', string)
                    #     # print(string)
                    if re.search('interfacevlanif3', re.sub(' ', '', string.lower())):
                        # print (string)
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[1]['ipStart'] + ' ' + str(
                            int(ipPlans[1]['mark'])) + '\n', string)
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[1]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[1]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[1]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[1]['ipEnd'] + '\n', string)

                    if re.search('interfacevlanif4', re.sub(' ', '', string.lower())) and not re.search(
                            'interfacevlanif409', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[2]['ipStart'] + ' ' + str(
                            int(ipPlans[2]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[2]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[2]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[2]['ipEnd'] + '\n', string)
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[2]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                    if re.search('interfacevlanif5', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[3]['ipStart'] + ' ' + str(
                            int(ipPlans[3]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[3]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[3]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[3]['ipEnd'] + '\n', string)
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[3]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                    if re.search('interfacevlanif6', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[4]['ipStart'] + ' ' + str(
                            int(ipPlans[4]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[4]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[4]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[4]['ipEnd'] + '\n', string)
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[4]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                    if re.search('interfacevlanif4094', re.sub(' ', '', string.lower())):
                        try:
                            temp = re.search('(dhcp\s*server\s*gateway-list[\s\S]*?\n)', string).groups()[0]
                            string = re.sub(temp, 'dhcp server gateway-list  ' + ipPlans[5]['ipStart'] + '\n',
                                            string)
                        except:
                            pass
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[5]['ipStart'] + ' ' + str(
                            int(ipPlans[5]['mark'])) + '\n', string)
                        temp = re.findall('dhcp\s*server\s*ip-range[\s\S]*?\n', string)
                        string = re.sub(temp[0], 'dhcp server ip-range ' + '.'.join(ipPlans[5]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[5]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +ipPlans[5]['ipEnd'] + '\n', string)
                        # print(string)
                        temp = re.search('(dhcp\s*server\s*option[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, option + '\n', string)
                    if re.search('interfacegigabitethernet0/0/1', re.sub(' ', '', string.lower())) and re.search(
                            'address', string.lower()):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[6]['ipStart'].split('-')[0] + ' ' + str(
                            int(ipPlans[9]['mark'])) + '\n', string)
                    #     # print(string)
                    if re.search('interfacegigabitethernet0/0/2', re.sub(' ', '', string.lower())) and re.search(
                            'address', string.lower()):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[7]['ipStart'] + ' ' + str(
                            int(ipPlans[7]['mark'])) + '\n', string)
                    if re.search('接口区域', string):
                        string = '————————————————————————\n'
                        string += '接口区域划分：\n\n'
                        string += firewall
                    if re.search('接口配置', string):
                        string += fwPortInfos
                    if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string)and not re.search('用户配置', string):
                        string = re.sub('//[\s\S]*?\n', '\n', string)
                    f.write(re.sub('\r', '', string))
                    string = ''

        if string.strip() !='' and string.strip()[-1] != '#':
            if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string)and not re.search('用户配置', string):
                string = re.sub('//[\s\S]*?\n', '\n', string)
            f.write(re.sub('\r', '', string))
        if Flag78:
            f.write(re.sub('\r', '', '\n' + vlan78Info))


def vlan78(ipPlans, DNS):
    # 返回vlan78
    flag7 = False
    flag8 = False
    ip7 = ip8 = ''
    for ipPlan in ipPlans:
        if str(ipPlan['vlan']).strip() == '7':
            flag7 = True
            ip7 = ipPlan
        if str(ipPlan['vlan']).strip() == '8':
            flag8 = True
            ip8 = ipPlan

    string = '\n————————————————————————————\n'
    string += '三网合一配置：非必须配置，可选项，根据职场场景和需求配置\n'
    string += '#\n'
    string += '''vlan batch 7 to 8
#
vlan 7
 description LifeTraining-WiFi
vlan 8
 description FreeWiFi-WiFi
#\n'''
    string1 = ''
    if flag7 and flag8:
        string1 = 'port trunk allow-pass vlan 2 to 8 4094'
        string += '''interface Vlanif7
 ip binding vpn-instance LAN
 description LifeTraining-WiFi-Gateway\n'''
        string += ' ip address ' + ip7['ipStart'].strip() + '  ' + str(int(ip7['mark'])) + '\n' + ' dhcp select interface\n'
        string += ' dhcp server ip-range  ' + '.'.join(ip7['ipStart'].split('.')[:-1]) + '.' + str(int(ip7['ipStart'].split('.')[-1].strip()) + 1) + '  ' + ip7['ipEnd'] + '\n'
        string += ' dhcp server lease day 0 hour 2 minute 0\n'
        string += ' dhcp server dns-list ' + DNS + '\n' + '#\n'
        string += '''interface Vlanif8
 ip binding vpn-instance LAN      
 description FreeWiFi-WiFi-Gateway  \n'''
        string += ' ip address ' + ip8['ipStart'].strip() + '  ' + str(
            int(ip8['mark'])) + '\n' + ' dhcp select interface\n'
        string += ' dhcp server ip-range  ' + '.'.join(ip8['ipStart'].split('.')[:-1]) + '.' + str(
            int(ip8['ipStart'].split('.')[-1].strip()) + 1) + '  ' + ip8['ipEnd'] + '\n'
        string += ' dhcp server lease day 0 hour 2 minute 0\n'
        string += ' dhcp server dns-list ' + DNS + '\n' + '#\n'
        string += 'acl number 3900\n rule 5 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[0]['segment'] + ' ' + wildcardMark[
                       str(int(ipPlans[0]['mark']))] + '\n'
        string += ' rule 10 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[1]['segment'] + ' ' + wildcardMark[
                       str(int(ipPlans[1]['mark']))] + '\n'
        string += ' rule 15 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[2]['segment'] + ' ' + wildcardMark[
                       str(int(ipPlans[2]['mark']))] + '\n'
        string += ' rule 20 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[3]['segment'] + ' ' + wildcardMark[
                       str(int(ipPlans[3]['mark']))] + '\n'
        string += ' rule 25 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[4]['segment'] + ' ' + wildcardMark[
                       str(int(ipPlans[4]['mark']))] + '\n'
        string += ' rule 35 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ip7['segment'] + ' ' + \
                   wildcardMark[str(int(ip7['mark']))] + '\n'
        string += ' rule 40 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[6]['segment']+ ' 0.0.0.7  \n'
        string += ' rule 45 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[7]['segment'] + ' 0.0.0.7  \n'
        string += ''' rule 50 deny ip source 133.124.15.0 0.0.0.127 destination 10.0.0.0 0.255.255.255   
 rule 55 permit ip source 133.124.15.0 0.0.0.127 destination 172.20.145.195 0    
 rule 60 deny ip source 133.124.15.0 0.0.0.127 destination 14.3.12.0 0.0.0.3     
 rule 65 deny ip source 133.124.15.0 0.0.0.127 destination 172.20.0.0 0.0.255.255 
 rule 100 permit ip
 #
traffic classifier free_wifi_c 
 if-match acl 3900
#
traffic behavior free_wifi_b              
 permit
#
traffic policy free_wifi_geli 
 classifier free_wifi_c behavior free_wifi_b
#
vlan 8
 traffic-policy free_wifi_geli inbound    
#
'''
    elif flag7:
        string1 = 'port trunk allow-pass vlan 2 to 7 4094'
        string += '''interface Vlanif7
 ip binding vpn-instance LAN
 description LifeTraining-WiFi-Gateway\n'''
        string += ' ip address ' + ip7['ipStart'].strip() + '  ' + str(
            int(ip7['mark'])) + '\n' + ' dhcp select interface\n'
        string += ' dhcp server ip-range  ' + '.'.join(ip7['ipStart'].split('.')[:-1]) + '.' + str(
            int(ip7['ipStart'].split('.')[-1].strip()) + 1) + '  ' + ip7['ipEnd'] + '\n'
        string += ' dhcp server lease day 0 hour 2 minute 0\n'
        string += ' dhcp server dns-list ' + DNS + '\n' + '#\n'

    elif flag8:
        string1 = 'port trunk allow-pass vlan 2 to 6 8 4094'
        string += '''interface Vlanif8
 ip binding vpn-instance LAN      
 description FreeWiFi-WiFi-Gateway  \n'''
        string += ' ip address ' + ip8['ipStart'].strip() + '  ' + str(
            int(ip8['mark'])) + '\n' + ' dhcp select interface\n'
        string += ' dhcp server ip-range  ' + '.'.join(ip8['ipStart'].split('.')[:-1]) + '.' + str(
            int(ip8['ipStart'].split('.')[-1].strip()) + 1) + '  ' + ip8['ipEnd'] + '\n'
        string += ' dhcp server lease day 0 hour 2 minute 0\n'
        string += ' dhcp server dns-list ' + DNS + '\n' + '#\n'
        string += 'acl number 3900\n rule 5 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[0]['segment'] + ' ' + wildcardMark[
                      str(int(ipPlans[0]['mark']))] + '\n'
        string += ' rule 10 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[1]['segment'] + ' ' + wildcardMark[
                      str(int(ipPlans[1]['mark']))] + '\n'
        string += ' rule 15 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[2]['segment'] + ' ' + wildcardMark[
                      str(int(ipPlans[2]['mark']))] + '\n'
        string += ' rule 20 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[3]['segment'] + ' ' + wildcardMark[
                      str(int(ipPlans[3]['mark']))] + '\n'
        string += ' rule 25 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[4]['segment'] + ' ' + wildcardMark[
                      str(int(ipPlans[4]['mark']))] + '\n'
        string += ' rule 40 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[6]['segment'] + ' 0.0.0.7  \n'
        string += ' rule 45 deny ip source ' + ip8['segment'] + ' ' + wildcardMark[
            str(int(ip8['mark']))] + ' destination ' + ipPlans[7]['segment'] + ' 0.0.0.7  \n'
        string += ''' rule 50 deny ip source 133.124.15.0 0.0.0.127 destination 10.0.0.0 0.255.255.255   
 rule 55 permit ip source 133.124.15.0 0.0.0.127 destination 172.20.145.195 0    
 rule 60 deny ip source 133.124.15.0 0.0.0.127 destination 14.3.12.0 0.0.0.3     
 rule 65 deny ip source 133.124.15.0 0.0.0.127 destination 172.20.0.0 0.0.255.255 
 rule 100 permit ip
 #
traffic classifier free_wifi_c 
 if-match acl 3900
#
traffic behavior free_wifi_b              
 permit
#
traffic policy free_wifi_geli 
 classifier free_wifi_c behavior free_wifi_b
#
vlan 8
 traffic-policy free_wifi_geli inbound    
#
'''

    else:
        string1 = 'port trunk allow-pass vlan 2 to 6 4094'

    # print(string)
    return string, string1

if __name__ == '__main__':
    ipPlans =[{'segment': '133.146.28.0', 'ipStart': '133.146.28.1', 'ipEnd': '133.146.31.254', 'mark': 22, 'vlan': 2, 'use': 'WIFI'}, {'segment': '133.148.4.0', 'ipStart': '133.148.4.1', 'ipEnd': '133.148.4.126', 'mark': 25, 'vlan': 3, 'use': 'ZhiBo&PeiXun'}, {'segment': '133.148.4.128', 'ipStart': '133.148.4.129', 'ipEnd': '133.148.4.254', 'mark': 25, 'vlan': 4, 'use': 'PC'}, {'segment': '133.149.4.0', 'ipStart': '133.149.4.1', 'ipEnd': '133.149.4.126', 'mark': 25, 'vlan': 5, 'use': 'Security'}, {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 6, 'use': 'Other'}, {'segment': '133.150.1.0', 'ipStart': '133.150.1.1', 'ipEnd': '133.150.1.126', 'mark': 25, 'vlan': 4094, 'use': '接入交换机&AP管理'}, {'segment': '133.151.0.128', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25, 'vlan': 'CORE_TO_AR1', 'use': '设备互连'}, {'segment': '133.151.0.136', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25, 'vlan': 'CORE_TO_AR2', 'use': '设备互连'}, {'segment': '133.151.0.144', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25, 'vlan': 'CORE_TO_FW(WAN)', 'use': '设备互连'}, {'segment': '133.151.0.152', 'ipStart': '133.151.0.129', 'ipEnd': '133.151.0.254', 'mark': 25, 'vlan': 'CORE_TO_FW(LAN)', 'use': '设备互连'}, {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 8, 'use': 'Free-Wifi'}, {'segment': '133.149.4.128', 'ipStart': '133.149.4.129', 'ipEnd': '133.149.4.254', 'mark': 25, 'vlan': 7, 'use': 'zzzz'}]
    # fwFile = {'sysname': 'LIFE-FW-HN-ZZ-NYL-S2700-4F-06', 'fwFile': 'C:\\Users\\Ribbon\\Desktop\\平安2\\PingAnNet\\全场景标准配置脚本V1.7.2\\D类场景防火墙做核心.txt'}
    # dealABC(fwFile, ipPlans)

    fwportConnect = [{'0': 'GigabitEthernet1/0/3', '1': 'GigabitEthernet1/0/4', '2': 'Eth-Trunk1', '3': {'0': 'GigabitEthernet0/0/1', '1': 'GigabitEthernet0/0/2', '2': '上行(ETH-TRUNK1)', '3': 'Eth-Trunk1', 'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01'}}, {'0': 'GigabitEthernet1/0/5', '1': '', '2': '', '3': {'0': 'GigabitEthernet0/0/3', '1': 'GigabitEthernet0/0/3', '2': '单线上联', '3': 'GigabitEthernet1/0/5', 'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01'}}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]
    dns1 = '12.255.2.2'
    dns2 = '12.255.2.3'
    option = 'dhcp server option 43 sub-option 2 ip-address 119.18.231.27 116.204.99.68'
    # dealDE(fwFile, ipPlans, fwportConnect, dns1, dns2, option)
    fwFile = {'sysname': 'e','fwFile': 'C:\\Users\\Ribbon\\Desktop\\平安2\\PingAnNet\\全场景标准配置脚本V1.7.2\\E类场景防火墙做核心.txt'}
    # fwportConnect = [{'0': 'GigabitEthernet1/0/3.2', '1': '', '2': ''}, {'0': 'GigabitEthernet1/0/4.3', '1': '', '2': ''}, {'0': 'GigabitEthernet1/0/4.5', '1': '', '2': ''}, {'0': 'GigabitEthernet1/0/4.6', '1': '', '2': ''}, {'0': 'GigabitEthernet1/0/4.4094', '1': '', '2': ''}, {'0': 'GigabitEthernet1/0/3.4', '1': '', '2': ''}, {'0': '', '1': '', '2': ''}, {'0': '', '1': '', '2': ''}]
    dealDE(fwFile, ipPlans, fwportConnect, dns1, dns2, option)