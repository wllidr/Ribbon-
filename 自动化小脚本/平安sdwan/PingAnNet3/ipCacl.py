'''
    Author: Ribbon Huang
    Date : 2019 - 01 -05
    Desc:
        根据网段 和 掩码计算有效IP网段
'''
import sys; sys.path.append('.')
from IPy import IP

def ipip(a, ipSegment):
    try:
        ips = IP(a)
        for ip in ips:
            if ip == ips[1]:
                ipSegment.append(ip)
            elif ip == ips[-1]:
                ipSegment.append(ip)
            else :
                ipSegment.append(ip)
    except Exception as e:
        b = (a.split('/')[0]).split('.')
        a = b[0] + '.' + b[1] + '.' + b[2] + '.' + str(int(b[-1])-1) + '/' + a.split('/')[-1]
        ipip(a, ipSegment)

def ipBegin(inputip, start, end):
    end = -2 - end
    start = 1 + start
    ipSegment = []
    ipip(inputip, ipSegment)
    # print(ipSegment[start], ipSegment[end])
    return str(ipSegment[start]), str(ipSegment[end])

if __name__ == '__main__':
    inputip = '133.20.40.1/25'
    ipBegin(inputip, 0, 0)
    # inputip = '133.146.28.0/22'
    # ipBegin(inputip, 0, 0)