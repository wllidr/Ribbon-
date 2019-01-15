'''
    Date : 2019 - 01 -06
    Desc:
        核心文件输出
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

def dealSw(swFile, ipPlans, swportConnect, dns1, dns2, option):
    # vlan78
    DNS = dns1 + ' ' + dns2
    vlan78Info, other = vlan78(ipPlans, DNS)
    sysname = swFile['sysname']
    file = swFile['swFile']
    portInfos = swPortInfos(swportConnect, other)
    with open(sysname + '.txt', 'w') as f5:
        with open(file, 'rb') as f:
            string = ''
            for line in f:
                line = line.decode('gbk', 'ignore')
                string += line
                if line.strip() == '#':
                    if re.search('sysname[\s\S]*?\n', string):
                        string = re.sub('sysname[\s\S]*?\n', 'sysname ' + sysname + '\n', string)
                    if re.search('dhcpserverdns-list', re.sub(' ', '', string.lower())):
                        string = re.sub('dns-list[\s\S]*?\n', 'dns-list  ' + DNS + '\n', string)
                    if re.search('interfacevlanif2\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[0]['ipStart'] + ' ' + str(
                            int(ipPlans[0]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[0]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[0]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[0]['ipEnd'] + '\n', string)
                    if re.search('interfacevlanif3\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[1]['ipStart'] + ' ' + str(
                            int(ipPlans[1]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[1]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[1]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[1]['ipEnd'] + '\n', string)
                    if re.search('interfacevlanif4\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[2]['ipStart'] + ' ' + str(
                            int(ipPlans[2]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[2]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[2]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[2]['ipEnd'] + '\n', string)
                        # print(string)
                    if re.search('interfacevlanif5\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[3]['ipStart'] + ' ' + str(
                            int(ipPlans[3]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[3]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[3]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[3]['ipEnd'] + '\n', string)
                    #     # print(string)
                    if re.search('interfacevlanif6\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[4]['ipStart'] + ' ' + str(
                            int(ipPlans[4]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(
                            ipPlans[4]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[4]['ipStart'].split('.')[-1].strip()) + 1) + '  ' +
                                        ipPlans[4]['ipEnd'] + '\n', string)
                    if re.search('interfacevlanif4094', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[5]['ipStart'] + ' ' + str(
                            int(ipPlans[5]['mark'])) + '\n', string)
                        temp = re.search('(server\s*ip-range[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'server ip-range ' + '.'.join(ipPlans[5]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[5]['ipStart'].split('.')[-1].strip()) + 1) + '  ' + ipPlans[5]['ipEnd'] + '\n', string)
                        temp = re.search('(dhcp\s*server\s*option[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, option + '\n', string)
                    if re.search('interfaceeth-trunk126\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[8]['ipStart'] + ' ' + str(
                            int(ipPlans[8]['mark'])) + '\n', string)
                    if re.search('interfaceeth-trunk127\s', re.sub(' ', '', string.lower())):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[9]['ipStart'] + ' ' + str(
                            int(ipPlans[9]['mark'])) + '\n', string)
                    if re.search('interfacegigabitethernet1/0/20', re.sub(' ', '', string.lower())) and re.search(
                            'address', string.lower()):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[6]['ipStart'] + ' ' + str(
                            int(ipPlans[6]['mark'])) + '\n', string)
                    #     # print(string)
                    if re.search('interfacegigabitethernet2/0/20', re.sub(' ', '', string.lower())) and re.search(
                            'address', string.lower()):
                        temp = re.search('(ip\s*address[\s\S]*?\n)', string).groups()[0]
                        string = re.sub(temp, 'ip address ' + ipPlans[7]['ipStart'] + ' ' + str(
                            int(ipPlans[7]['mark'])) + '\n', string)
                    if re.search('network', re.sub(' ', '', string.lower())):
                        networks = re.findall('network[\s\S]*?\n', string)
                        for i in range(len(networks)):
                            string = re.sub(networks[i], '  network ' + ipPlans[6 + i]['segment'] + '  0.0.0.7 \n', string)
                    if re.search('route-static\s*vpn-instance', string):
                        temp = re.findall('(ip\s*route-static\s*[\s\S]*?\n)', string)
                        string = re.sub(temp[0], 'ip route-static vpn-instance LAN 0.0.0.0 0.0.0.0 ' + '.'.join(
                            ipPlans[6]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[6]['ipStart'].split('.')[-1].strip()) + 1) + ' preference 100 track nqa admin To_R1\n', string)
                        string = re.sub(temp[1], 'ip route-static vpn-instance LAN 0.0.0.0 0.0.0.0 ' + '.'.join(
                            ipPlans[7]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[7]['ipStart'].split('.')[-1].strip()) + 1) + ' preference 100 track nqa admin To_R2\n', string)
                        try:
                            string = re.sub(temp[2], 'ip route-static vpn-instance LAN 0.0.0.0 0.0.0.0 ' + '.'.join(
                                ipPlans[9]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[9]['ipStart'].split('.')[-1].strip()) + 1) + ' track nqa admin To_FW \n',string)
                        except:
                            pass
                    if re.search('nexthop', string):
                        temp = re.search('nexthop([\s\S]*?)\n', string).groups()[0]
                        string = re.sub(temp, ' ' + '.'.join(ipPlans[8]['ipStart'].split('.')[:-1]) + '.' + str(
                            int(ipPlans[8]['ipStart'].split('.')[-1].strip()) + 1) + '  track-nqa admin To_FW_PBR\n', string)
                    if re.search('unicast-server', string):
                        temp = re.findall('unicast-server[\s\S]*?\n', string)
                        string = re.sub(temp[0], ' unicast-server ' + '.'.join(ipPlans[6]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[6]['ipStart'].split('.')[-1].strip()) + 1) + ' vpn-instance WAN\n',string)
                        string = re.sub(temp[1], ' unicast-server ' + '.'.join(
                            ipPlans[7]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[7]['ipStart'].split('.')[-1].strip()) + 1) + ' vpn-instance WAN\n',string)
                    if re.search('destination-address', string):
                        if re.search('To_FW\s', string):
                            temp = re.search('destination-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp,'  ' + '.'.join(ipPlans[8]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[8]['ipStart'].split('.')[-1].strip()) + 1), string)
                            temp = re.search('source-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + ipPlans[9]['ipStart'].strip(), string)
                        if re.search('To_R1\s', string):
                            temp = re.search('destination-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + '.'.join(
                                ipPlans[6]['ipStart'].split('.')[:-1]) + '.' + str(
                                int(ipPlans[6]['ipStart'].split('.')[-1].strip()) + 1), string)
                            temp = re.search('source-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + ipPlans[6]['ipStart'], string)
                        if re.search('To_R2\s', string):
                            temp = re.search('destination-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + '.'.join(
                                ipPlans[7]['ipStart'].split('.')[:-1]) + '.' + str(
                                int(ipPlans[7]['ipStart'].split('.')[-1].strip()) + 1), string)
                            temp = re.search('source-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + ipPlans[7]['ipStart'], string)
                        if re.search('To_FW_PBR\s', string):
                            temp = re.search('destination-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp,'  ' + '.'.join(ipPlans[9]['ipStart'].split('.')[:-1]) + '.' + str(int(ipPlans[9]['ipStart'].split('.')[-1].strip()) + 1), string)
                            temp = re.search('source-address\s*ipv4([\s\S]*?)\n', string).groups()[0]
                            string = re.sub(temp, '  ' + ipPlans[8]['ipStart'], string)
                    if re.search('port\s*trunk\s*allow-pass\s*vlan', string):
                        string = re.sub('port\s*trunk\s*allow-pass\s*vlan[\s\S]*?\n', other + '\n', string)
                    if re.search('三网合一配置', string):
                        f5.write(re.sub('\r', '', vlan78Info))
                        break
                    if re.search('NTP配置', string):
                        string = portInfos + string
                    if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string) and not re.search('用户配置', string):
                        string = re.sub('//[\s\S]*?\n', '\n', string)
                    f5.write(re.sub('\r', '', string))
                    string = ''
            if string.strip() != '' and string.strip()[-1] != '#':
                if re.search('//[\s\S]*?\n', string) and not re.search('默认账号和密码查询网站', string) and not re.search('用户配置', string):
                    string = re.sub('//[\s\S]*?\n', '\n', string)
                f5.write(re.sub('\r', '', string))


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


def swPortInfos(swportConnect, other):
    # print(swportConnect)
    portInfos = '#\n'
    for port in swportConnect:
        if port['0'] != '' and port['1'] != '' and port['2'] != '':
            portInfos += 'interface ' + port['2'] + '\n'
            portInfos += ' description To-LAN-AccessSwitch-Eth_Trunk1' + '\n'
            portInfos += ' port link-type trunk\n' + ' undo port trunk allow-pass vlan 1\n'
            portInfos += ' ' + other + '\n'
            if port['mad'] != '':
                portInfos += ' mad relay\n'
            portInfos += '#\n'
            portInfos += 'interface ' + port['0'] + '\n'
            portInfos += ' description To-AccessSwitch-' + '-'.join(port['3']['sysname'].split('-')[-3:]) + '-Gi' + port['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + port['0'].split('t')[-1] + '\n'
            portInfos += ' eth-trunk ' + port['2'].split('k')[-1] + '\n' + '#\n'
            portInfos += 'interface ' + port['1'] + '\n'
            portInfos += ' description To-AccessSwitch-' + '-'.join(port['3']['sysname'].split('-')[-3:]) + '-Gi' + port['3']['1'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + port['0'].split('t')[-1] + '\n'
            portInfos += ' eth-trunk ' + port['2'].split('k')[-1] + '\n' + '#\n'
        elif port['0'] != '' and port['1'] == '' and port['2'] == '':
            portInfos += 'interface ' + port['0'] + '\n'
            portInfos += ' undo portswitch\n'
            portInfos += ' description To-AccessSwitch-' + '-'.join(port['3']['sysname'].split('-')[-3:]) + '-Gi' + port['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + port['0'].split('t')[-1] + '\n'
            portInfos += ''' port link-type trunk
 undo port trunk allow-pass vlan 1\n'''
            portInfos += ' ' + other + '\n'
            if port['mad'] != '':
                portInfos += ' mad relay\n'
            portInfos += '#\n'
        elif port['0'] == '' and port['1'] != '' and port['2'] == '':
            portInfos += 'interface ' + port['1'] + '\n'
            portInfos += ' undo portswitch\n'
            if port['3']['0'] != '':
                portInfos += ' description To-AccessSwitch-' + '-'.join(port['3']['sysname'].split('-')[-3:]) + '-Gi' + port['3']['0'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + port['1'].split('t')[-1] + '\n'
            else:
                portInfos += ' description To-AccessSwitch-' + '-'.join(port['3']['sysname'].split('-')[-3:]) + '-Gi' + port['3']['1'].split('t')[-1] + '__From-CoreSwitch-01-Gi' + port['1'].split('t')[-1] + '\n'
            portInfos += ''' port link-type trunk
 undo port trunk allow-pass vlan 1\n'''
            portInfos += ' ' + other + '\n'
            if port['mad'] != '':
                portInfos += ' mad relay\n'
            portInfos += '#\n'
    # print(portInfos)
    return portInfos

if __name__ == '__main__':
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
    dns1 = '12.255.2.2'
    dns2 = '12.255.2.3'
    option = 'dhcp server option 43 sub-option 2 ip-address 119.18.231.27 116.204.99.68'
    swFile = {'sysname': 'LIFE-SW-HN-ZZ-NYL-S5720EI','swFile': r'C:\Users\Ribbon\Desktop\平安2\PingAnNet\全场景标准配置脚本V1.7.2\CORE-SW-S5720EI-有FW-堆叠.txt'}
    swportConnect = [{'mad': 'mad','0': 'GigabitEthernet1/0/3', '1': 'GigabitEthernet1/0/4', '2': 'Eth-Trunk1', '3': {'0': 'GigabitEthernet0/0/1', '1': 'GigabitEthernet0/0/2', '2': '上行(ETH-TRUNK1)', '3': 'Eth-Trunk1', 'sysname': 'LIFE-SW-HN-ZZ-NYL-S2750-2F-01'}}, {'mad': '','0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}, {'0': '', '1': '', '2': '', '3': ''}]
    other = 'port trunk allow-pass vlan 2 to 8 4094'

    # swPortInfos(swportConnect, other)
    dealSw(swFile, ipPlans, swportConnect, dns1, dns2, option)