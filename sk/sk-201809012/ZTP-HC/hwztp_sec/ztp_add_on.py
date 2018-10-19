#!/usr/bin/env python
import httplib
import urllib
import string
import re
import xml.etree.ElementTree as etree
import os
import stat
import logging
import traceback
import hashlib
import socket
import ops
import signal
import logging.handlers

from urlparse import urlparse
from urlparse import urlunparse
from time import sleep
from datetime import datetime

# error code
OK  = 0
ERR = 1

# provisional vlan and vlanif ip
VLAN_ID   = '4063'
VLANIF_IP = '10.255.255.254/24'

LOG_FILE_EXECUTE = 'ztp_addon.log'

def log_init(log_file = None, level = logging.DEBUG):
    """Initialize log config."""
    ilogger = logging.getLogger()
    if log_file:
        hdlr = logging.handlers.RotatingFileHandler(log_file, maxBytes = 512 * 1024, backupCount = 0)
    else:
        hdlr = logging.StreamHandler()

    fmts = '%(asctime)s %(levelname)-8s %(filename)s:%(lineno)s %(message)s'
    datefmts = '%b %d %Y %H:%M:%S'
    fmt = logging.Formatter(fmts, datefmts)
    hdlr.setFormatter(fmt)
    ilogger.addHandler(hdlr)
    ilogger.setLevel(level)
    #exceptions get silently ignored 
    logging.raiseExceptions = 0

def log_rotate():
    """Rotate log immediately"""
    
    ilogger = logging.getLogger()
    for hdlr in ilogger.handlers[:]:
        if isinstance(hdlr, logging.handlers.RotatingFileHandler):
            hdlr.doRollover()
    return

def log_fini():
    """Finalize log, the log file will be removed."""
    ilogger = logging.getLogger()
    for hdlr in ilogger.handlers[:]:
        if type(hdlr) == logging.handlers.RotatingFileHandler:
            if os.path.exists(hdlr.baseFilename):
                os.remove(hdlr.baseFilename)        # remove log file
            if hdlr.backupCount > 0:
                # remove backup log files
                for i in range(1, hdlr.backupCount + 1):
                    dfn = "%s.%d" % (hdlr.baseFilename, i)
                    if os.path.exists(dfn):
                        os.remove(dfn)

        ilogger.removeHandler(hdlr)
    ilogger.addHandler(logging.NullHandler())       # to prevent an error message being output

class OPSConnection(object):
    """docstring for OPSConnection"""
    def __init__(self, host,port=80):
        self.host = host
        self.port = port
        self.headers={
            "Content-type": "application/xml",
            "Accept":       "application/xml"
        }
        self.conn = httplib.HTTPConnection(self.host, self.port)

    def close(self):
        self.conn.close()

    def create(self,uri,req_data):
        ret = self._rest_call("POST", uri, req_data)
        return ret


    def get(self, uri, req_data=None):
        ret = self._rest_call("GET", uri, req_data)
        return ret

    def set(self,uri,req_data):
        ret = self._rest_call("PUT",uri,req_data)
        return ret


    def _rest_call(self, method, uri, req_data):
        """REST call"""

        if req_data == None:
            body = ""
        else:
            body = req_data
        self.conn.request(method, uri, body, self.headers)
        response = self.conn.getresponse()
        ret = (response.status, response.reason, response.read())
        return ret

class OPIExecError(Exception):
    """OPI executes error."""
    pass

class ZTPErr(Exception):
    """ZTP error."""
    pass

class UserAbort(KeyboardInterrupt):
    """User abort ZTP exception."""
    pass



def signal_handler(signum, frame):
    """Signal handler to ignore a signal"""
    pass


def file_exist(ops_conn, file_path):
    """Returns True if file_path refers to an existing file, otherwise returns False"""
    uri = "/vfm/dirs/dir"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<dir>
    <fileName>$fileName</fileName>
</dir>
''')
    req_data = str_temp.substitute(fileName = file_path)
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to list information about the file "%s"' % file_path)

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "fileName", namespaces)
    if elem is None:
        return False

    return True

def del_file(ops_conn, file_path):
    """Delete a file permanently"""
    if file_path is None or file_path is '':
        return

    #logging.warning("Delete file %s permanently", file_path)
    uri = "/vfm/deleteFileUnRes"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<deleteFileUnRes>
    <fileName>$filePath</fileName>
</deleteFileUnRes>
''')
    req_data = str_temp.substitute(filePath = file_path)
    try:
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to delete the file "%s" permanently' % file_path)

    except Exception, reason:
        #logging.error(reason)
        return
        
def read_csv(csvName):

    """
    This is a function read csvfile and return three tables from this csvfile

    """
    rows1 = []
    rows2 = []
    rows3 = []
    device = {}
    table1 = True
    table2 = False
    table3 = False
    for line in open(csvName):
        line = line.strip('\n')
        line = line.strip('\r')
        rows = line.split(',')

        if (rows[0] == "L2link------"):
            table1 = False;
            table2 = True;
            continue
        if (rows[0] == "L3link------"):
            table2 = False;
            table3 = True;
            continue
        if table1 is True:
            rows1.append(rows)
        elif table2 is True:
            rows2.append(rows)
        elif table3 is True:
            rows3.append(rows)

    for index in range(len(rows1[0])):
        if index > len(rows1[1]):
            device[rows1[0][index]] = ''
        else:
            device[rows1[0][index]] = rows1[1][index]

    return device,rows2,rows3

def get_port_trunk_status(ops_conn,portName):
    """
    get_port_trunk_status

    @param1 ops_conn: this is ops instance
    @param2 portName: this is port name

    """
    uri = "/ifm/interfaces/interface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
    <interface>
        <ifName>$portName</ifName>
        <ifTrunkIfName></ifTrunkIfName>
    </interface>
''')
    req_data = str_temp.substitute(portName = portName)
    ret, _, rsp_data = ops_conn.get(uri, req_data)

    root_elem = etree.fromstring(rsp_data)
    namespace = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:ifTrunkIfName'
    elem = root_elem.find(uri,namespace)
    if elem is None or elem.text is None:
        return OK
    else:
         return ERR

def ops_execute_vlan_info(portName):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + portName)
    rsp_data = _ops.cli.execute(handle,"display this | include vlan")
    for paras in rsp_data:
        paras_item = str(paras)
        if paras_item.find("vlan") != -1:
            return ERR
    ret = _ops.cli.close(handle)
    return OK

def ops_execute_undo_portswitch_info(portName):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + portName)
    rsp_data = _ops.cli.execute(handle,"display this | include undo portswitch")
    for paras in rsp_data:
        paras_item = str(paras)
        if paras_item.find("undo portswitch") != -1:
            return ERR
    ret = _ops.cli.close(handle)
    return OK




def check_port_status(ops_conn,portgroup_message):
    """
    check_port_status

    @param1 ops_conn: this is ops instance
    @param2 portgroup_message: this is portgroup information table

    """
    result_flag = True
    portgroup_message_aftercheck = []
    port_chackfailed = []

    logging.info("Now starting check port status")

    for item in portgroup_message:
        port_status_flag = True
        portName = item['portIndex']
        logging.info("check " + portName + " status")

        ret = ops_execute_vlan_info(portName)
        if ret == ERR:
            port_status_flag = False
            result_flag = False
            logging.error("check " + portName + " vlan status fail")
        else:
            logging.info("check " + portName + " vlan status success")

        ret = get_port_trunk_status(ops_conn,portName)
        if ret == ERR:
            port_status_flag = False
            result_flag = False
            logging.error("check " + portName + " trunk status fail")
        else:
            logging.info("check " + portName + " trunk status success")

        ret = ops_execute_undo_portswitch_info(portName)
        if ret == ERR:
            port_status_flag = False
            result_flag = False
            logging.error("check " + portName + " undo portswitch fail")
        else:
            logging.info("check " + portName + " undo portswitch success")

        if port_status_flag == True:
            portgroup_message_aftercheck.append(item)
        else:
            port_chackfailed.append(portName)

    logging.info("portgroup message after check: %s", portgroup_message_aftercheck)
    logging.info("Check port status end")

    return result_flag, portgroup_message_aftercheck,port_chackfailed

def set_port_temp_vlan(ops_conn,portName,tempVlanNumber):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + portName)
    ret = _ops.cli.execute(handle,"port default vlan " + tempVlanNumber)
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"com")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    _ops.cli.close(handle)
    return OK


def create_temp_vlan(ops_conn,vlanId):
    
    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    ret = _ops.cli.execute(handle,"vlan " + vlanId)
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"com")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR

    _ops.cli.close(handle)
    return OK
    
def create_temp_vlanif(ops_conn, if_name, vlan_num):
    """create one vlan interface"""
    logging.info("create one vlan interface, vlan interface number: %s", str(vlan_num))
    uri = "/ifm/interfaces/interface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<interface>
    <ifName>$ifName</ifName>
    <ifPhyType>Vlanif</ifPhyType>
    <ifNumber>$ifNumber</ifNumber>
    <ifAdminStatus>up</ifAdminStatus>
</interface>
''')

    req_data = str_temp.substitute(ifName = if_name, ifNumber = vlan_num)
    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

def set_interface_ip(ops_conn, if_name, ip_addr, netmask):
    """Set interface IP address."""
    logging.info("Set interface %s: IP=%s SubnetMask=%s", if_name, ip_addr, netmask)
    uri = "/ifm/interfaces/interface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<interface>
<ifName>$ifName</ifName>
<ifmAm4>
    <am4CfgAddrs>
        <am4CfgAddr>
            <ifIpAddr>$ipAddr</ifIpAddr>
            <subnetMask>$subnetMask</subnetMask>
            <addrType>main</addrType>
        </am4CfgAddr>
    </am4CfgAddrs>
</ifmAm4>
</interface>
''')
    req_data = str_temp.substitute(ifName = if_name, ipAddr = ip_addr, subnetMask = netmask)
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        logging.info("Set interface %s: IP=%s SubnetMask=%s error", if_name, ip_addr, netmask)
        return ERR
    return OK

def set_interface_ipadd(ops_conn,IfIndex,IpAddress,IpAddressMask):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + IfIndex)
    ret = _ops.cli.execute(handle,"undo port default vlan " + VLAN_ID)
    logging.info(ret)
    ret = _ops.cli.execute(handle,"undo portswitch")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"dldp enable")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"ip address " + IpAddress + ' ' + IpAddressMask)
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    # ret = _ops.cli.execute(handle,"ospf network-type p2p")
    # logging.info(ret)
    # if ret[2].lower() != 'success':
    #     _ops.cli.close(handle)
    #     return ERR
    ret = _ops.cli.execute(handle,"com")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.close(handle)

    return OK


def ops_execute_set_dhcp_relay(ops_conn,vlanIfNum,dhcpSeverIp,giAddr):
    """
    set_dhcp_relay

    @param1 vlanIfNum: this is vlanIf Num
    @param2 dhcpSeverIp: this is dhcp Sever Ip
    @param3 giAddr: this is gate Addr

    """

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + vlanIfNum)
    ret = _ops.cli.execute(handle,"dhcp select relay")
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"dhcp relay binding server ip " + dhcpSeverIp)
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
    ret = _ops.cli.execute(handle,"dhcp relay gateway " + giAddr)
    logging.info(ret)
    if ret[2].lower() != 'success':
        _ops.cli.close(handle)
        return ERR
        
    ret = _ops.cli.execute(handle,"comm")
    logging.info(ret)
        
    _ops.cli.close(handle)

    return OK

def get_system_name(ops_conn):
    logging.info("Get the system name...")
    uri = "/system/systemInfo"
    req_data =  \
'''<?xml version="1.0" encoding="UTF-8"?>
<systemInfo>
    <sysName/>
</systemInfo>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to get the system name')

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:sysName'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return None
    return elem.text
    
def get_netmask(maskNum):
    mask = ['0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0']
    for i in range(maskNum):
        mask[i] = '1'
    netmask = ''
    tempnum = 0
    for i in range(32):
        tempnum = tempnum*2 + int(mask[i])
        if i == 31:
            netmask = netmask + str(tempnum)
        elif (i + 1)%8 == 0:
            netmask = netmask + str(tempnum) + '.'
            tempnum = 0

    return netmask
    
def get_wildcardmask(maskNum):
    mask = ['0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0']
    for i in range(maskNum, 32, 1):
        mask[i] = '1'
    wildcardmask = ''
    tempnum = 0
    for i in range(32):
        tempnum = tempnum*2 + int(mask[i])
        if i == 31:
            wildcardmask = wildcardmask + str(tempnum)
        elif (i + 1)%8 == 0:
            wildcardmask = wildcardmask + str(tempnum) + '.'
            tempnum = 0

    return wildcardmask
    
def add_ospf(ops_conn,ip):

    # _ops = ops.ops()
    #
    # handle, err_desp  = _ops.cli.open()
    # _ops.cli.execute(handle,"sys")
    # _ops.cli.execute(handle,"ospf 1")
    # _ops.cli.execute(handle,"area 0.0.0.0")
    # ret = _ops.cli.execute(handle,"network " + ip.split('/')[0] + ' ' + get_wildcardmask(int(ip.split('/')[1])))
    # logging.info(ret)
    # if ret[2].lower() != 'success':
    #     _ops.cli.close(handle)
    #     return ERR
    # ret = _ops.cli.execute(handle,"comm")
    # logging.info(ret)
    # if ret[2].lower() != 'success':
    #     _ops.cli.close(handle)
    #     return ERR
    #
    # _ops.cli.close(handle)

    return OK
    
def exit_ospf(ops_conn,ip):

    # _ops = ops.ops()
    #
    # handle, err_desp  = _ops.cli.open()
    # _ops.cli.execute(handle,"sys")
    # _ops.cli.execute(handle,"ospf 1")
    # _ops.cli.execute(handle,"area 0.0.0.0")
    # ret = _ops.cli.execute(handle,"undo network " + ip.split('/')[0] + ' ' + get_wildcardmask(int(ip.split('/')[1])))
    # if ret[2].lower() != 'success':
    #     _ops.cli.close(handle)
    #     return ERR
    # ret = _ops.cli.execute(handle,"comm")
    # if ret[2].lower() != 'success':
    #     _ops.cli.close(handle)
    #     return ERR
    #
    # _ops.cli.close(handle)

    return OK
   

def set_port_temp_info(ops_conn,rows1,portgroup_message_aftercheck):
    """
    set_port_temp_info
    """

    set_port_temp_flag = True
    ret = create_temp_vlan(ops_conn,VLAN_ID)
    if ret == ERR:
        set_port_temp_flag = False
        logging.error("create temp vlan fail")
    else:
        logging.info("create temp vlan success")

    vlanIfNum = "vlanif" + VLAN_ID
    
    ret = create_temp_vlanif(ops_conn, 'Vlanif' + VLAN_ID, VLAN_ID)
    if ret == ERR:
        set_port_temp_flag = False
        logging.error("create temp vlanif fail")
    else:
        logging.info("create temp vlanif success")
        
    ret = set_interface_ip(ops_conn, 'Vlanif' + VLAN_ID, VLANIF_IP.split('/')[0], get_netmask(int(VLANIF_IP.split('/')[1])))
    if ret == ERR:
        set_port_temp_flag = False
        logging.error("set temp vlanif ip fail")
    else:
        logging.info("set temp vlanif ip success")

    if "TRUE" in rows1["Dhcp Relay Server"]:
        ret = ops_execute_set_dhcp_relay(ops_conn, vlanIfNum,rows1['Dhcp Server Ip'],VLANIF_IP.split('/')[0])
        if ret == ERR:
            set_port_temp_flag = False
            logging.error("set dhcp relay fail")
        else:
            logging.info("set dhcp relay success")

    for i in range(len(portgroup_message_aftercheck)):
        ret = set_port_temp_vlan(ops_conn,portgroup_message_aftercheck[i]['portIndex'],VLAN_ID)
        if ret == ERR:
            set_port_temp_flag = False
            logging.error("set port %s temp vlan fail", portgroup_message_aftercheck[i]['portIndex'])
        else:
            logging.info("set port %s temp vlan success", portgroup_message_aftercheck[i]['portIndex'])
            
    # ret = add_ospf(ops_conn,VLANIF_IP)
    # if ret == ERR:
    #     set_port_temp_flag = False
    #     logging.error("set ospf network ip fail")
    # else:
    #     logging.info("set ospf network ip success")

    if set_port_temp_flag == False:
        return ERR
    return OK

def set_lldp_enable(ops_conn):

    """
    set_lldp_enable

    @param ops_conn: this is ops instance

    """

    uri = "/lldp/lldpSys"
    req_data = \
'''<?xml version="1.0" encoding="UTF-8"?>
    <lldpSys>
        <lldpEnable>enabled</lldpEnable>
    </lldpSys>
'''
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

def check_lldp_status_sysname(ops_conn,portName):
    """
    check_lldp_status_sysname

    @param1 ops_conn: this is ops instance
    @param2 portName: this is L2 port Name

    """

    uri = "/lldp/lldpInterfaces/lldpInterface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<lldpInterface>
    <ifName>$portName</ifName>
    <lldpNeighbors>
        <lldpNeighbor>
            <systemName/>
        </lldpNeighbor>
    </lldpNeighbors>
</lldpInterface>
''')

    req_data = str_temp.substitute(portName = portName)

    ret, _, rsp_data = ops_conn.get(uri, req_data)
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:lldpNeighbors' + '/vrp:lldpNeighbor' + '/vrp:systemName'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return None
    logging.info("get lldp neighbor sysname success,the name is %s, port is %s", elem.text, portName)
    return OK

def get_lldp_port_sysname(ops_conn,portName):
    """
    check_lldp_status_sysname

    @param1 ops_conn: this is ops instance
    @param2 portName: this is L2 port Name

    """

    uri = "/lldp/lldpInterfaces/lldpInterface"
    str_temp = string.Template(
        '''<?xml version="1.0" encoding="UTF-8"?>
        <lldpInterface>
            <ifName>$portName</ifName>
            <lldpNeighbors>
                <lldpNeighbor>
                    <systemName/>
                </lldpNeighbor>
            </lldpNeighbors>
        </lldpInterface>
        ''')

    req_data = str_temp.substitute(portName = portName)

    ret, _, rsp_data = ops_conn.get(uri, req_data)
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:lldpNeighbors' + '/vrp:lldpNeighbor' + '/vrp:systemName'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return ""
    logging.info("get lldp neighbor sysname success,the name is %s, port is %s", elem.text, portName)
    return elem.text
    
def check_lldp_status_mngtip(ops_conn,portinfo):

    uri = "/lldp/lldpInterfaces/lldpInterface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<lldpInterface>
    <ifName>$portName</ifName>
    <lldpNeighbors>
        <lldpNeighbor>
            <managementAddresss/>
        </lldpNeighbor>
    </lldpNeighbors>
</lldpInterface>
''')

    req_data = str_temp.substitute(portName = portinfo['portIndex'])
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:lldpNeighbors' + '/vrp:lldpNeighbor' + '/vrp:managementAddresss' + '/vrp:managementAddress' + '/vrp:manAddr'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return None
    logging.info("get lldp neighbor mngtip success,the ip is %s, port is %s", elem.text, portinfo['portIndex'])
    for i in range(len(portinfo['peerMgntIp'])):
        if elem.text == portinfo['peerMgntIp'][i]:
            return OK
    return None

def set_bgp_info(ops_conn, rows1, ifIndexMsg):
    # isSpine = False
    # if rows1['Device Role']!=None:
    #     isSpine= rows1['Device Role'].lower().strip()=='spine'
    # ipAddress     = ifIndexMsg['peerLpbackIp'].split('/')[0]
    # ipAddress     = ifIndexMsg['connIp'].split('/')[0]
    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    if rows1['Device Role'].lower().strip()=='spinerr':
        ipAddress     = ifIndexMsg['peerLpbackIp'].split('/')[0]
        logging.info("Set bgp peer, AS Number is  %s: IP=%s ", rows1['As Num'], ipAddress)
        _ops.cli.execute(handle,"bgp " + rows1['As Num']+' instance evpn')
        _ops.cli.execute(handle,"peer " + ipAddress + " as-number " + rows1['As Num'])
        _ops.cli.execute(handle,"peer " + ipAddress + " connect-interface LoopBack1")
        _ops.cli.execute(handle,"peer " + ipAddress + " description  " + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
        _ops.cli.execute(handle,"peer " + ipAddress + " bfd min-tx-interval 200 min-rx-interval 200 detect-multiplier 5")
        _ops.cli.execute(handle,"peer " + ipAddress + " bfd enable")
        _ops.cli.execute(handle,"l2vpn-family evpn")
        _ops.cli.execute(handle,"peer " + ipAddress + " enable")
        _ops.cli.execute(handle,"peer " + ipAddress + " advertise irb")
        _ops.cli.execute(handle,"peer " + ipAddress + " reflect-client")
        ipAddress     = ifIndexMsg['remoteIp'].split('/')[0]
        _ops.cli.execute(handle,"bgp 64605")
        _ops.cli.execute(handle,"peer " + ipAddress + " group FB1-Leaf")
        # print('JxinBain spinerr description :' + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
        logging.info('JxinBain spinerr description :' + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
        _ops.cli.execute(handle,"peer " + ipAddress + " description  " + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
    elif rows1['Device Role'].lower().strip()=='spine':
        ipAddress     = ifIndexMsg['remoteIp'].split('/')[0]
        _ops.cli.execute(handle, "bgp 64605")
        _ops.cli.execute(handle, "peer " + ipAddress + " group FB1-Leaf")
        # print('JxinBain spine description :' + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
        logging.info('JxinBain spine description :' + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
        _ops.cli.execute(handle, "peer " + ipAddress + " description  " + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
    # elif rows1['Device Role'].lower().strip()=='leaf':
    #     ipAddress     = ifIndexMsg['peerLpbackIp'].split('/')[0]
    #     logging.info("Set bgp peer, AS Number is  %s: IP=%s ", rows1['As Num'], ipAddress)
    #     _ops.cli.execute(handle,"bgp " + rows1['As Num']+' instance evpn')
    #     _ops.cli.execute(handle,"peer " + ipAddress + " as-number " + rows1['As Num'])
    #     _ops.cli.execute(handle,"peer " + ipAddress + " connect-interface LoopBack0")
    #     _ops.cli.execute(handle,"l2vpn-family evpn")
    #     _ops.cli.execute(handle,"peer " + ipAddress + " enable")
    #     _ops.cli.execute(handle,"peer " + ipAddress + " advertise irb")
    #     ipAddress     = ifIndexMsg['remoteIp'].split('/')[0]
    #     _ops.cli.execute(handle,"bgp 101")
    #     _ops.cli.execute(handle,"peer " + ipAddress + " group Spine")
    #     _ops.cli.execute(handle,"peer " + ipAddress + " as-number 102")
    #     _ops.cli.execute(handle,"peer " + ipAddress + " description  " + get_lldp_port_sysname(ops_conn,ifIndexMsg['portIndex']))
    _ops.cli.execute(handle,"comm")
    _ops.cli.close(handle)
    return  OK
    

def check_lldp_info(ops_conn,rows1,portgroup):
    flag = True
    while flag:
        flag = False
        for i in range(len(portgroup)):
            portName = portgroup[i]['portIndex']
            ret1 = check_lldp_status_sysname(ops_conn,portName)
            ret2 = check_lldp_status_mngtip(ops_conn,portgroup[i])
            if ret1 == OK and ret2 == OK:
                #set l3 config
                for j in range(len(portgroup)):
                    if portgroup[i]['grpNo'] == portgroup[j]['grpNo']:
                        set_l3_info(ops_conn, portgroup[j])
                        set_bgp_info(ops_conn, rows1, portgroup[j])
                #delete these ports
                portgroup = [ x for x in portgroup if x['grpNo'] != portgroup[i]['grpNo'] ]
                flag = True
                break
    return portgroup

def set_dhcp_enable(ops_conn):

    uri = "/dhcp/common/dhcpCommonCfg"
    req_data = \
'''<?xml version="1.0" encoding="UTF-8"?>
    <dhcpCommonCfg>
        <dhcpEnable>true</dhcpEnable>
    </dhcpCommonCfg>
'''

    ret,_,rsp_data = ops_conn.set(uri,req_data)
    if ret != httplib.OK:
        return ERR
    return OK
    
def _get_ztpStatus(ops_conn):
    """Get the environment variable: ztpStatus"""
    logging.info("Get the environment variable: ztpStatus...")
    uri = "/devm/ztps/ztp"
    req_data = '''<?xml version="1.0" encoding="UTF-8"?>
<ztp>
    <ztpStatus/>
</ztp>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        logging.error('Failed to get ztpStatus')
        return 1
        
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "ztpStatus", namespaces)
    if elem is None:
        logging.error('Failed to get ztpStatus for no "ztpStatus" element')
        return 1
        
    return elem.text
    
    
def _get_ztpEndFlag(ops_conn):
    """Get the environment variable: ztpEndFlag"""
    logging.info("Get the environment variable: ztpEndFlag...")
    uri = "/devm/ztps/ztp"
    req_data = '''<?xml version="1.0" encoding="UTF-8"?>
<ztp>
    <ztpEndFlag/>
</ztp>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        logging.error('Failed to get ztpEndFlag')
        raise OPIExecError('Failed to get ztpEndFlag')

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "ztpEndFlag", namespaces)
    if elem is None:
        logging.error('Failed to get ztpEndFlag for no "ztpEndFlag" element')
        raise OPIExecError('Failed to get ztpEndFlag for no "ztpEndFlag" element')

    return elem.text
    
def _set_ztpEndFlag(ops_conn, endFlag):
    """Get the environment variable: ztpEndFlag"""
    logging.info("set the environment variable: ztpEndFlag...")
    uri = "/devm/ztps/ztp"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<ztp>
    <ztpStatus>$ztpStatus</ztpStatus>
    <ztpEndFlag>$endFlag</ztpEndFlag>
</ztp>
''')
    ztpStatus = _get_ztpStatus(ops_conn)
    req_data = str_temp.substitute(ztpStatus = ztpStatus,endFlag = endFlag)
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        logging.error('Failed to set ztpEndFlag')


def delete_temp_vlan(ops_conn):
    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"undo int vlanif " + VLAN_ID)
    _ops.cli.execute(handle,"undo vlan " + VLAN_ID)
    _ops.cli.execute(handle,"comm")
    ret = _ops.cli.close(handle)
    return OK
    
def save_config(ops_conn):
    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    choice = {"Continue": "y", "continue": "y"}
    _ops.cli.execute(handle,"save",choice)
    _ops.cli.close(handle)
    return OK
    
def delete_temp_info(ops_conn):
    # exit_ospf(ops_conn,VLANIF_IP)
    delete_temp_vlan(ops_conn)
    return OK

def set_l3_info(ops_conn,ifIndexMsg):
    
    ifIndex       = ifIndexMsg['portIndex']
    ipAddress     = ifIndexMsg['connIp'].split('/')[0]
    ipAddressMask = ifIndexMsg['connIp'].split('/')[1]

    ret = set_interface_ipadd(ops_conn,ifIndex,ipAddress,get_netmask(int(ipAddressMask)))
    if ret == ERR:
        logging.info("Set interface %s: IP=%s error", ifIndex, ipAddress)

    set_interface_description(ops_conn,ifIndexMsg)

    # add_ospf(ops_conn,ifIndexMsg['connIp'])
    
    return  OK

def set_interface_description(ops_conn,ifIndexMsg):
    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"interface " + ifIndexMsg['portIndex'])
    _ops.cli.execute(handle,"description To_" + ifIndexMsg['peerSysname'] + "_" +ifIndexMsg['remoteIp'].split('/')[0]+'_' + ifIndexMsg['peerPortIndex'])
    _ops.cli.execute(handle,"comm")

    _ops.cli.close(handle)

    return OK

def change_lower(dict1):
    dict2 = {}
    for key in dict1:
        dict2[key.lower()] = dict1[key]
    return dict2 

def get_portgroup_message(rows1, rows2, rows3):
    """
    get ztp port group messages and put it in an array
    such as:
    [{'grpNo': 'GRP_CE39', 'portIndex': '40GE1/0/15', 'connIp': '192.168.10.3/30'},
     {'grpNo': 'GRP_CE38', 'portIndex': '40GE1/0/1', 'connIp': '192.168.10.8/30'}]
    """
    portgroup_message = []
    indexA = 0
    indexB = 0
    portIndexA = 0
    portIndexB = 0
    grpNoIndex = 0
    rows1 = change_lower(rows1)
    for index in range(len(rows2[0])):
        if rows2[0][index] == "A NEIndex":
            indexA = index
        if rows2[0][index] == "B NEIndex":
            indexB = index
        if rows2[0][index] == "A Port Index":
            portIndexA = index
        if rows2[0][index] == "B Port Index":
            portIndexB = index
        if rows2[0][index] == "ZTP GrpNO.":
            grpNoIndex = index

    # add grpNo and portIndex
    for item in rows2[1:]:
        if item[grpNoIndex] != '':
            if rows1['sysname'] == item[indexA]:
                d = dict(portIndex=item[portIndexA],grpNo=item[grpNoIndex],connIp='',peerSysname=item[indexB],peerPortIndex=item[portIndexB],peerMgntIp=[],peerLpbackIp='',remoteIp = '')
                portgroup_message.append(d)
            elif rows1['sysname'] == item[indexB]:
                d = dict(portIndex=item[portIndexB],grpNo=item[grpNoIndex],connIp='',peerSysname=item[indexA],peerPortIndex=item[portIndexA],peerMgntIp=[],peerLpbackIp='',remoteIp = '')
                portgroup_message.append(d)
                
    # add connection ip
    ifIndexA = 0
    ifIndexB = 0
    ifPortIndexA = 0
    ifPortIndexB = 0
    connIpA = 0
    connIpB = 0
    peerMgntIndex = 0
    peerLp1Index = 0
    for index in range(len(rows3[0])):
        if rows3[0][index] == "A NEIndex":
            ifIndexA = index
        if rows3[0][index] == "B NE Index":
            ifIndexB = index
        if rows3[0][index] == "A IF Index":
            ifPortIndexA = index
        if rows3[0][index] == "B IF Index":
            ifPortIndexB = index
        if rows3[0][index] == "A ConnIPv4":
            connIpA = index
        if rows3[0][index] == "B ConnIPv4":
            connIpB = index
        if rows3[0][index] == "Peer Device MgntIPV4":
            peerMgntIndex = index
        if rows3[0][index] == "Peer Device Loopback1 IPV4":
            peerLp1Index = index
    for i in range(len(portgroup_message)):
        for item in rows3[1:]:
            if item[ifIndexA] == rows1['sysname'] and item[ifPortIndexA] == portgroup_message[i]['portIndex']:
                portgroup_message[i]['connIp'] = item[connIpA]
                portgroup_message[i]['peerLpbackIp'] = item[peerLp1Index]
                portgroup_message[i]['remoteIp'] = item[connIpB]
                #if stack, may have more than one mgnt ip
                for j in range(len(item[peerMgntIndex].split(';'))):
                    portgroup_message[i]['peerMgntIp'].append(item[peerMgntIndex].split(';')[j].split('/')[0])
                break
            elif item[ifIndexB] == rows1['sysname'] and item[ifPortIndexB] == portgroup_message[i]['portIndex']:
                portgroup_message[i]['connIp'] = item[connIpB]
                portgroup_message[i]['peerLpbackIp'] = item[peerLp1Index]
                portgroup_message[i]['remoteIp'] = item[connIpA]
                for j in range(len(item[peerMgntIndex].split(';'))):
                    portgroup_message[i]['peerMgntIp'].append(item[peerMgntIndex].split(';')[j].split('/')[0])
                break
    return portgroup_message

def undo_shutdown_port(ops_conn,portName):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + portName)
    _ops.cli.execute(handle,"undo shutdown")
    _ops.cli.execute(handle,"comm")
    ret = _ops.cli.close(handle)
    return OK
    
def delete_logfile(ops_conn):

    _ops = ops.ops()
    handle,_ = _ops.cli.open()
    choice = {"Continue": "y", "continue": "y"}
    _ops.cli.execute(handle,"del /u " + LOG_FILE_EXECUTE,choice)
    _ops.cli.close(handle)
    
    return OK
    
def clear_ops_conf(ops_conn):
    _ops = ops.ops()
    handle,_ = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"ops")
    _ops.cli.execute(handle,"undo script-assistant python ztp_add_on.py")
    _ops.cli.execute(handle,"comm")
    ret = _ops.cli.close(handle)

# def get_port_description(port_info):
#     return 'TO_'+port_info[4]+'_'+port_info[6].split('/')[0]+'_'+port_info[5]
#
# def set_port_description(ops_conn,port_info):
#     _ops = ops.ops()
#
#     handle, err_desp  = _ops.cli.open()
#     _ops.cli.execute(handle,"sys")
#     _ops.cli.execute(handle,"int " + port_info[1])
#     _ops.cli.execute(handle,"description "+get_port_description(port_info))
#     _ops.cli.execute(handle,"comm")
#     ret = _ops.cli.close(handle)
#     return OK

def set_layer_interface_description(ops_conn,local_port,description):
    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"interface " + local_port)
    _ops.cli.execute(handle,"description " + description)
    _ops.cli.execute(handle,"comm")

    _ops.cli.close(handle)

    return OK

def set_same_layer_interface_description(ops_conn,rows1,rows2):
    sysIndex = rows1['NE Index']
    for index in range(1,len(rows2)):
        line_list = rows2[index]
        if line_list[0] ==sysIndex and line_list[3].strip().lower().find('spine')==-1:
            local_interface_name = line_list[0].strip()
            local_interface_port = line_list[1].strip()
            local_eth_trunk_port = line_list[2]
            remote_interface_name = line_list[3].strip()
            remote_interface_port = line_list[4].strip()
            remote_eth_trunk_port = line_list[5]
            if(local_eth_trunk_port!=None and isinstance(local_eth_trunk_port,str) and local_eth_trunk_port.strip()!=''):
                set_layer_interface_description(ops_conn,local_eth_trunk_port,'To_%s_%s'%(remote_interface_name,remote_eth_trunk_port))
            set_layer_interface_description(ops_conn,local_interface_port,'To_%s_%s'%(remote_interface_name,remote_interface_port))
        elif line_list[3]==sysIndex and line_list[0].strip().lower().find('spine')==-1:
            remote_interface_name = line_list[0].strip()
            remote_interface_port = line_list[1].strip()
            remote_eth_trunk_port = line_list[2]
            local_interface_name = line_list[3].strip()
            local_interface_port = line_list[4].strip()
            local_eth_trunk_port = line_list[5]
            if(local_eth_trunk_port!=None and isinstance(local_eth_trunk_port,str) and local_eth_trunk_port.strip()!=''):
                set_layer_interface_description(ops_conn,local_eth_trunk_port,'To_%s_%s'%(remote_interface_name,remote_eth_trunk_port))
            set_layer_interface_description(ops_conn,local_interface_port,'To_%s_%s'%(remote_interface_name,remote_interface_port))
        else:
            pass

def main_proc(ops_conn):

    delete_logfile(ops_conn)
    log_init(LOG_FILE_EXECUTE, logging.INFO)

    logging.info("Now starting the add on process...")

    #step 0: make sure the csv file is exist and then read it to get portgroup message
    sysName = get_system_name(ops_conn)
    if sysName == None:
        logging.error("Get system name failed")
        return ERR

    #csvName = 'addon_' + sysName + '.csv'
    csvName = sysName + '.csv'
    if not os.path.exists('/opt/vrpv8/home/' + csvName):
        logging.error("There is no file named %s, check AC please" % csvName)
        return ERR

    rows1,rows2,rows3 = read_csv(csvName)
    portgroup_message = get_portgroup_message(rows1, rows2, rows3)

    # step 1: check port status
    # step 1.1: make sure there is no config such as vlan, undo portswitch, Eth-Trunk in these ports
    logging.info("Check port status...")
    result_flag, portgroup_message_aftercheck,port_chackfailed = check_port_status(ops_conn,portgroup_message)
    if result_flag == False:
        logging.error("These ports have some service configuration: %s, they will not be treated as ports for ZTP", port_chackfailed)

    # step 1.2: undo shutdown all ports in the portgroup
    for i in range(len(portgroup_message_aftercheck)):
        undo_shutdown_port(ops_conn,portgroup_message_aftercheck[i]['portIndex'])

    ret = set_dhcp_enable(ops_conn)
    if ret == ERR:
        logging.error("set dhcp enable fail")
    else:
        logging.info("set dhcp enable success")

    # step 2: if current mode is in band,config temp vlan,vlanif ip,dhcp relay and so on
    if "IN_BAND" in rows1["bandMgntMode"]:
        logging.info("Current mode is in band and starting to set some port temp infos")
        ret = set_port_temp_info(ops_conn,rows1,portgroup_message_aftercheck)
        if ret == ERR:
            logging.error("set port temp info fail")
        else:
            logging.info("set port temp info success")

    # step 2.1: set the others device which in the same layer interface description(inclue eth-trunk)
    # set_same_layer_interface_description(ops_conn,rows1,rows2)

    # step 3: query neighbor information and ztp endflag
    logging.info("Starting to get neighbor informations and ztp endflag")
    ret = set_lldp_enable(ops_conn)
    if ret == ERR:
        logging.error("set lldp enable fail")
    else:
        logging.info("set lldp enable success")
    sleep(10)
    portgroup_not_end = portgroup_message_aftercheck
    check_num = 1
    while True:
        logging.info("port group before %s times check: %s", check_num, portgroup_not_end)
        # step 4: set if work mode l3 and config connection ip
        portgroup_not_end = check_lldp_info(ops_conn,rows1,portgroup_not_end)
        if len(portgroup_not_end) == 0:
            logging.info("check lldp neighbors information success")
            break
        else:
            logging.info("port group after %s times check: %s", check_num, portgroup_not_end)

        ztpEndFlag = _get_ztpEndFlag(ops_conn)
        if ztpEndFlag == 0:
            logging.info("get ztp end flag")
            _set_ztpEndFlag(ops_conn, 1)
            break

        if check_num == 600:
            logging.error("Execute for more than 10 hours, exit process...")
            break
        logging.info("Can't get all ports' neighbors or ztp end flag, retry to get again after 60s...")
        check_num = check_num + 1
        sleep(60)

    #step 5: ZTP end, clean temp configuration and residual files
    logging.info("Now starting to clean up the environment...")
    if "IN_BAND" in rows1["bandMgntMode"]:
        ret == delete_temp_info(ops_conn)
        if ret == OK:
            logging.info("delete temp info success")
            
    save_config(ops_conn)
        
    if file_exist(ops_conn, csvName):
        del_file(ops_conn, csvName)
        
    clear_ops_conf(ops_conn)

    return OK


# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : ops_condition               
# Date Created    : 2018-2-27         
# Author          : 356912            
# History         :                    
# Date                Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def ops_condition(_ops):

    _ops.timer.countdown("e1", 1)
    
    _ops.correlate("e1")
    
# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : ops_execute               
# Date Created    : 2016-2-27          
# Author          : Author             
# History         :                    
# Date                Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def ops_execute(_ops): 
    host = "localhost"
    
    try:
        ops_conn = OPSConnection(host)
        ret = main_proc(ops_conn)

    except OPIExecError,reason:
        ret = ERR

    except ZTPErr, reason:
        ret = ERR

    except Exception, reason:

        traceinfo = traceback.format_exc()
        ret = ERR

    except UserAbort:
        ret = ERR

    finally:
        ops_conn.close()

    return ret

if __name__ == '__main__':
    main()