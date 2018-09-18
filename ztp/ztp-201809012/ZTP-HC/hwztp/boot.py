#md5sum=""
#!/usr/bin/env python

"""
Zero Touch Provisioning (ZTP) enables devices to automatically load version files including system software,
patch files, configuration files and so on when the device starts up, the devices to be configured must be
new devices or have no configuration files.

This is a Zero Touch Provisioning sample script.
"""

import sys
import string
import re
import signal
import httplib
import urllib
import xml.etree.ElementTree as etree
import logging
import os
import ops

from time import sleep


# error code
OK          = 0
ERR         = 1

#Parameters of aaa user
USERNAME      = 'netconf'
# USERPASSWORD  = 'Changeme@123'
USERPASSWORD  = 'Huawei@123'
USERGROUP     = "manage-ug"

#Parameters of callhome configuration
# 12.255.3.248  192.168.6.2
AC_ADDRESS    = '12.255.3.248'
AC_PORT       = '10020'
NETCONFNAME   = "callHomeAc"

# Max seconds for waiting user input
HWOPS_INPUT_TIMEOUT        = 10

# all the interface types existing on device which may be has neighbor
IFTYPE_LIST = ['100GE', '40GE', '25GE', '10GE', 'GEBrief']

# CSV file obtained from AC with device information
AC_CSVNAME = 'Agile-Controller-DCN.csv'

class OPSConnection(object):
    """Make an OPS connection instance."""

    def __init__(self, host, port = 80):
        self.host = host
        self.port = port
        self.headers = {
            "Content-type": "application/xml",
            "Accept":       "application/xml"
            }

        self.conn = httplib.HTTPConnection(self.host, self.port)

    def close(self):
        """Close the connection"""
        self.conn.close()

    def create(self, uri, req_data):
        """Create a resource on the server"""
        ret = self._rest_call("POST", uri, req_data)
        return ret

    def delete(self, uri, req_data):
        """Delete a resource on the server"""
        ret = self._rest_call("DELETE", uri, req_data)
        return ret

    def get(self, uri, req_data = None):
        """Retrieve a resource from the server"""
        ret = self._rest_call("GET", uri, req_data)
        return ret

    def set(self, uri, req_data):
        """Update a resource on the server"""
        ret = self._rest_call("PUT", uri, req_data)
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
class BootError(Exception):
    """ZTP error."""
    pass

class UserAbort(KeyboardInterrupt):
    """User abort ZTP exception."""
    pass
    
# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : prompt_user_abort
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def prompt_user_abort(ops_conn):
    """Prompt user abort info, will raise a KeyboardInterrupt exception if user input CTRL+C"""
    # Ask if user want to abort ZTP and continue with normal setup.
    try:
        while True:
            line = raw_input("Press CTRL+C to abort Zero Touch Provisioning "
                             "in {} seconds...".format(HWOPS_INPUT_TIMEOUT))
            signal.signal(signal.SIGINT, signal_handler)
            if line is '':
                # input timeout or user press enter key
                break
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal_handler)
        if file_exist(ops_conn, 'boot.pyc'):
            del_file(ops_conn, 'boot.pyc')    # delete .pyc file        
        print('')   # print a newline after CTRL+C
        raise UserAbort('User abort')

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : file_exist
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def file_exist(ops_conn, file_path, dir_path = None):
    """Returns True if file_path refers to an existing file, otherwise returns False"""
    uri = "/vfm/dirs/dir"
    str_temp_1 = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<dir>
    <fileName>$fileName</fileName>
</dir>
''')
    str_temp_2 = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<dir>
    <dirName>$dirName</dirName>
    <fileName>$fileName</fileName>
</dir>
''')

    if dir_path:
        req_data = str_temp_2.substitute(dirName = dir_path, fileName = file_path)
    else:
        req_data = str_temp_1.substitute(fileName = file_path)
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        return False

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "fileName", namespaces)
    if elem is None:
        return False

    return True

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : del_file
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def del_file(ops_conn, file_path):
    """Delete a file permanently"""
    if file_path is None or file_path is '':
        return

    logging.info("Delete file %s permanently", file_path)
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
        logging.error(reason)

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : run_other_py
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def run_other_py(ops_conn,filename):
    """ZTP script execution"""
    print("Starting %s script execution..." % filename)
    moduleName,_ = os.path.splitext(filename)
    dir_name = os.getcwd()
    sys.path.append("/opt/vrpv8/home/")
    code = '''
if '%s' in sys.modules.keys():
    reload(sys.modules['%s'])
import %s
ret = %s.main()
''' % (moduleName, moduleName, moduleName, moduleName)
    exec(code)
    return ret


def signal_handler(signum, frame):
    """Signal handler to ignore a signal"""
    pass

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : _del_rsa_peer_key
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def _del_rsa_peer_key(ops_conn, key_name):
    """Delete RSA peer key configuration"""
    logging.info("Delete RSA peer key %s", key_name)
    uri = "/rsa/rsaPeerKeys/rsaPeerKey"
    root_elem = etree.Element('rsaPeerKey')
    etree.SubElement(root_elem, 'keyName').text = key_name
    req_data = etree.tostring(root_elem, "UTF-8")
    try:
        ret, _, _ = ops_conn.delete(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to delete RSA peer key')

    except Exception, reason:
        logging.error(reason)

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : _del_sshc_rsa_key
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def _del_sshc_rsa_key(ops_conn, server_name, key_type = 'RSA'):
    """Delete SSH client RSA key configuration"""
    uri = "/sshc/sshCliKeyCfgs/sshCliKeyCfg"
    root_elem = etree.Element('sshCliKeyCfg')
    etree.SubElement(root_elem, 'serverName').text = server_name
    etree.SubElement(root_elem, 'pubKeyType').text = key_type
    req_data = etree.tostring(root_elem, "UTF-8")
    try:
        ret, _, _ = ops_conn.delete(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to delete SSH client RSA key')

    except Exception, reason:
        logging.error(reason)

    _del_rsa_peer_key(ops_conn, server_name)

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : _set_sshc_first_time
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def _set_sshc_first_time(ops_conn, switch):
    """Set SSH client attribute of authenticating user for the first time access"""
    if switch not in ['Enable', 'Disable']:
        return ERR

    logging.info('Set SSH client first-time enable switch = %s', switch)
    uri = "/sshc/sshClient"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<sshClient>
    <firstTimeEnable>$enable</firstTimeEnable>
</sshClient>
''')
    req_data = str_temp.substitute(enable = switch)
    ret, _, _ = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        if switch == 'Enable':
            raise OPIExecError('Failed to enable SSH client first-time')
        else:
            raise OPIExecError('Failed to disable SSH client first-time')

    return OK

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : _sftp_download_file
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def _sftp_download_file(ops_conn, fileserverIp,filename,userName,password,xftp_port):
    """
    _sftp_download_file

    @param1 ops_conn: this is ops instance
    @param2 fileserverIp: the file server ip address
    @param3 filename:     the file name
    @param4 userName:     the ftp username
    @param5 password:     the ftp password

    """
    _set_sshc_first_time(ops_conn, 'Enable')
    uri = "/sshc/sshcConnects/sshcConnect"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<sshcConnect>
    <HostAddrIPv4>$fileserverIp</HostAddrIPv4>
    <serverPort>$serverPort</serverPort>
    <commandType>get</commandType>
    <userName>$username</userName>
    <password>$password</password>
    <remoteFileName>$filename</remoteFileName>
    <identityKey>ssh-rsa</identityKey>
    <transferType>SFTP</transferType>
</sshcConnect>
''')

    req_data = str_temp.substitute(fileserverIp = fileserverIp, serverPort = xftp_port, username = userName, password = password,
                                   filename = filename)

    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        print('Failed to download file "%s" using SFTP' % filename)
        ret = ERR
    else:
        print('Download file "%s" successfully'  % filename)
        ret = OK

    _del_sshc_rsa_key(ops_conn, fileserverIp)
    _set_sshc_first_time(ops_conn, 'Disable')
    return ret

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : read_csv
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def read_csv():
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
    for line in open(AC_CSVNAME):
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

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : set_lldp_enable
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def set_lldp_enable(ops_conn):

    """
    set_lldp_enable style

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

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : set_snetconf_server_enable
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def set_snetconf_server_enable(ops_conn):

    """
    set_snetconf_server_enable

    @param ops_conn: this is ops instance

    """

    uri = "/sshs/sshServer"
    req_data = \
'''<?xml version="1.0" encoding="UTF-8"?>
    <sshServer>
        <snetconfEnable>Enable</snetconfEnable>
    </sshServer>
'''
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : create_aaa_user
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def create_aaa_user(ops_conn):
    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"aaa")
    _ops.cli.execute(handle,"local-user " + USERNAME + " password irreversible-cipher " + USERPASSWORD)
    _ops.cli.execute(handle,"local-user " + USERNAME + " level 3")
    _ops.cli.execute(handle,"local-user " + USERNAME + " user-group " + USERGROUP)
    _ops.cli.execute(handle,"local-user " + USERNAME + " service-type ssh")
    _ops.cli.execute(handle,"com")
    ret = _ops.cli.close(handle)
    return OK

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : create_ssh_user
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def create_ssh_user(ops_conn):

    """
    create_ssh_user

    @param ops_conn: this is ops instance

    """

    uri = "/sshs/sshUserCfgs/sshUserCfg"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
        <sshUserCfg operation="create">
            <userName>$userName</userName>
            <authType>all</authType>
            <sftpDir>flash:/</sftpDir>
            <sshServiceType>all</sshServiceType>
        </sshUserCfg>
''')
    req_data = str_temp.substitute(userName = USERNAME)
    ret, _, rsp_data = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : set_call_home
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def set_call_home(ops_conn,sysName,netconfName,AC_address,AC_port):

    """
    set_call_home

    @param1 ops_conn: this is ops instance
    @param2 sysName: this is sysname
    @param3 netconfName: this is netconfName
    @param4 AC_address: this is AC IP address
    @param5 AC_port: this is AC port

    """

    uri = "/sshs/callHomes/callHome"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<callHome>
    <callHomeName>$sysName</callHomeName>
    <sshEndpoints>
        <sshEndpoint operation="create">
            <endpointName>$netconfName</endpointName>
            <address>$AC_address</address>
            <port>$AC_port</port>
        </sshEndpoint>
    </sshEndpoints>
</callHome>
''')
    req_data = str_temp.substitute(sysName = sysName,netconfName = netconfName,AC_address = AC_address,AC_port = AC_port)
    ret, _, rsp_data = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : change_lower
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def change_lower(dict1):
    dict2 = {}
    for key in dict1:
        dict2[key.lower()] = dict1[key]
    return dict2

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : get_port_identity_sysname
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def get_port_identity_sysname(ops_conn, intername):
    """Get neibor port identity, return sysName"""
    uri = "/lldp/lldpInterfaces/lldpInterface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<lldpInterface>
    <ifName>$ifname</ifName>
    <lldpNeighbors>
        <lldpNeighbor>
            <identityTlv>
                <identity/>
            </identityTlv>
        </lldpNeighbor>
    </lldpNeighbors>
</lldpInterface>
''')
    req_data = str_temp.substitute(ifname = intername)
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('get port "%s" identity failed' % ifname)
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:lldpNeighbors' + '/vrp:lldpNeighbor' + '/vrp:identityTlv' + '/vrp:identity'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return None
    return elem.text

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : get_port_status
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def get_port_status(ops_conn,name):
    """Get port description, return description"""
    uri = "/ifm/interfaces/interface"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<interface>
    <ifName>$ifName</ifName>
    <ifDynamicInfo>
        <ifPhyStatus></ifPhyStatus>
    </ifDynamicInfo>
</interface>
''')
    req_data = str_temp.substitute(ifName = name)
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('get port "%s" staus failed' % name)
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:ifDynamicInfo' + '/vrp:ifPhyStatus'
    elem = root_elem.find(uri, namespaces)
    if elem is None:
        return None
    return elem.text

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : get_interfaces_by_if_type
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def get_interfaces_by_if_type(ops_conn, if_type):
    """Get interfaces with specified interface type."""
    #logging.debug('Get all %s interfaces', if_type)
    uri = "/ifm/interfaces"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<interfaces>
    <interface>
        <ifName/>
        <ifPhyType>$ifPhyType</ifPhyType>
    </interface>
</interfaces>
''')
    req_data = str_temp.substitute(ifPhyType = if_type)
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to get the information of interfaces')
    if_name_list = []
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    for interface in root_elem.findall(uri + 'interface', namespaces):
        elem = interface.find("vrp:ifName", namespaces)
        if elem is None:
            break
        if_name_list.append(elem.text)
    return if_name_list
    
# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : get_up_port_list
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def get_up_port_list(ops_conn, iftype_list):

    ifnames = []    # all the interface names existing on device
    up_list = []    # all the up interface list

    for iftype in iftype_list:
        namelist = get_interfaces_by_if_type(ops_conn, iftype)
        if len(namelist) > 0:
            ifnames += namelist
    
    if len(ifnames) > 0:
        for ifname in ifnames:
            port_status = get_port_status(ops_conn, ifname)
            if port_status == 'up' :
                up_list.append(ifname)
    logging.info("All up ports: %s", str(up_list))
    return up_list

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : get_sysname_by_identity
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def get_sysname_by_identity(ops_conn, iftype_list):
    """Get current device sysName by neighber port identity"""
    up_list = get_up_port_list(ops_conn, iftype_list)
    if len(up_list) > 0:
        for ifname in up_list:
            sysName = get_port_identity_sysname(ops_conn, ifname)
            if (sysName is not None):
                logging.info("sysName get from port inentity is %s", sysName)
                return sysName
    logging.info("Can not get sysName from port inentity")
    return None
    
def set_system_name(ops_conn, sysname):
    uri = "/system/systemInfo"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<systemInfo>
    <sysName>$sysName</sysName>
</systemInfo>
''')
    req_data = str_temp.substitute(sysName = sysname)
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

def set_lldp_disable(ops_conn):

    """
    set_lldp_enable style

    @param ops_conn: this is ops instance

    """

    uri = "/lldp/lldpSys"
    req_data = \
'''<?xml version="1.0" encoding="UTF-8"?>
    <lldpSys>
        <lldpEnable>disabled</lldpEnable>
    </lldpSys>
'''
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK

def set_snetconf_server_disable(ops_conn):

    """
    set_snetconf_server_disable

    @param ops_conn: this is ops instance

    """

    uri = "/sshs/sshServer"
    req_data = \
'''<?xml version="1.0" encoding="UTF-8"?>
    <sshServer>
        <snetconfEnable>Disable</snetconfEnable>
    </sshServer>
'''
    ret, _, rsp_data = ops_conn.set(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK


def delete_aaa_user(ops_conn):
    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"aaa")
    _ops.cli.execute(handle,"undo local-user " + USERNAME)
    _ops.cli.execute(handle,"com")
    ret = _ops.cli.close(handle)
    return OK

def delete_ssh_user(ops_conn):

    """
    delete_ssh_user

    @param ops_conn: this is ops instance

    """

    uri = "/sshs/sshUserCfgs/sshUserCfg"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
        <sshUserCfg operation="delete">
            <userName>$userName</userName>
        </sshUserCfg>
''')
    req_data = str_temp.substitute(userName = USERNAME)
    ret, _, rsp_data = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        return ERR
    return OK


def delete_call_home(ops_conn):
    _ops = ops.ops()
    handle, err_desp = _ops.cli.open()
    choice = {"Continue": "y", "continue": "y", "exiting": "y"}
    _ops.cli.execute(handle,"sys",None)
    _ops.cli.execute(handle,"netconf",None)
    _ops.cli.execute(handle,"undo callhome huawei",choice)
    _ops.cli.execute(handle,"com",None)
    _ops.cli.close(handle)
    ret = _ops.cli.close(handle)
    return OK

def delete_initial_py(ops_conn,file_name):
    if file_exist(ops_conn, file_name):
        del_file(ops_conn, file_name)
    if file_exist(ops_conn, file_name + 'c'):
        del_file(ops_conn, file_name + 'c')

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : clean_boot_config
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def clean_boot_config(ops_conn):
    set_lldp_disable(ops_conn)
    set_snetconf_server_disable(ops_conn)
    delete_aaa_user(ops_conn)
    delete_ssh_user(ops_conn)
    _set_sshc_first_time(ops_conn, 'Disable')
    delete_call_home(ops_conn)
    set_system_name(ops_conn, 'HUAWEI')
    delete_initial_py(ops_conn,"initial.py")

# ----------------------------------------------------------------------------------------------------------------------
# Func Name       : main_proc
# Date Created    : 2018-01-24
# Author          : h00356912
# History         :
# Date           Author                      Modification
# ----------------------------------------------------------------------------------------------------------------------
def main_proc(ops_conn):
    """Main processing"""

    # lldp enable
    ret = set_lldp_enable(ops_conn)
    if ret == ERR:
        logging.error("set lldp enable failed")
        raise BootError("Set lldp enable failed")
    else:
        logging.info("set lldp enable success")
        print "Info: Set lldp enable success"

    # netconf enable
    ret = set_snetconf_server_enable(ops_conn)
    if ret == ERR:
        logging.error("set snetconf server enable failed")
        raise BootError("Set snetconf server enable failed")
    else:
        logging.info("set snetconf server enable success")
        print "Info: Set snetconf server enable success"

    #create aaa user
    ret = create_aaa_user(ops_conn)
    if ret == ERR:
        logging.error("create aaa user failed")
        raise BootError("Create aaa user failed")
    else:
        logging.info("create aaa user success")
        print "Info: Create aaa user success"

    #create ssh user
    ret = create_ssh_user(ops_conn)
    if ret == ERR:
        logging.error("create ssh user failed")
        raise BootError("Create ssh user failed")
    else:
        logging.info("create ssh user success")
        print "Info: Create ssh user success"

    #set ssh client first-time enable
    ret = _set_sshc_first_time(ops_conn, 'Enable')
    if ret == ERR:
        logging.error("set ssh client first-time enable failed")
        raise BootError("Set ssh client first-time enable failed")
    else:
        logging.info("set ssh client first-time enable success")
        print "Info: Set ssh client first-time enable success"
        
    if os.path.exists('/opt/vrpv8/home/' + AC_CSVNAME):
        del_file(ops_conn, AC_CSVNAME)

    #get sysName
    print "Info: Now starting to get sysname..."
    sleep(10)
    outSpineTag = False
    cnt = 0
    identitySysName = None
    while True:
        if cnt == 3:
            logging.error("Get sysname failed")
            print "Warning: Get sysname failed and continue script process"
            outSpineTag = True
            break
        identitySysName = get_sysname_by_identity(ops_conn, IFTYPE_LIST)
        if (identitySysName is not None):
            logging.info("Get sysname success, sysname is %s" % identitySysName)
            print ("Info: Get sysname success, sysname is %s" % identitySysName)
            ret = set_system_name(ops_conn, identitySysName)
            if ret == ERR:
                logging.error("Set system name failed")
                raise BootError("Set system name failed")
            else:
                logging.info("Set system name success")
                print "Info: Set system name success"
            break
        else:
            print "Try to get sysname again ..."
            cnt = cnt + 1
            sleep(10)

    #call home
    print "Info: Now starting to set call home..."
    ret = set_call_home(ops_conn,"huawei",NETCONFNAME,AC_ADDRESS,AC_PORT)
    if ret == ERR:
        logging.error("set call home failed")
        raise BootError("Set call home failed")
        return ERR
    else:
        logging.info("set call home success")
        print "Info: set call home success"

    print "Info: Now starting to download csv file..."
    sleep(120)
    cnt = 0
    while True:
        if cnt == 3:
            logging.error("CSV file is not exist")
            raise IOError('open csv file error')
        if os.path.exists('/opt/vrpv8/home/' + AC_CSVNAME):
            print "Info: Download csv file successfully"
            break
        else:
            cnt = cnt + 1
            print "Try to read csv file again ..."
            sleep(60)

    rows1,rows2,rows3 = read_csv()
    rows1 = change_lower(rows1)
    
    sysName = rows1['ne index']
    if outSpineTag == True:
        #Check if current device is Out-of-band spine
        print rows1['device role'].find('Spine')
        print rows1['bandmgntmode'].find('OUT_OF_BAND')
        if rows1['device role'].find('Spine') < 0 or rows1['bandmgntmode'].find('OUT_OF_BAND') < 0:
            print "Error: current device is not out-of-band spine"
            logging.error("Current device is not out-of-band spine")
            return ERR
        else:
            ret = set_system_name(ops_conn, sysName)
            if ret == ERR:
                logging.error("Set system name failed")
                raise BootError("Set system name failed")
            else:
                logging.info("Set system name success")
                print "Info: Set system name success"
    else:
        #Check the identity of current device
        if sysName != identitySysName:
            print "Error: check system name failed"
            logging.error("Check sysname failed, get from neighbor is %s and get from csv is %s", identitySysName, sysName)
            return ERR
        

    #starting to download initial.py and execute it
    xftp_ip        = rows1['xftp server ip']
    xftp_user      = rows1['xftp server user']
    xftp_password  = rows1['xftp server passwd']
    xftp_port      = rows1['xftp server port']

    logging.info(rows1['xftp server ip'])
    logging.info(rows1['xftp server user'])
    logging.info(rows1['xftp server passwd'])
    logging.info(rows1['xftp server port'])
    logging.info('-----------------------------')
    logging.info(rows1)
    logging.info('-----------------------------')
    logging.info(rows2)
    logging.info('-----------------------------')
    logging.info(rows3)

    filename = "initial.py"

    ret = _sftp_download_file(ops_conn, xftp_ip,filename,xftp_user,xftp_password,xftp_port)
    if ret == OK:
        ret = run_other_py(ops_conn,filename)
    else:
        ret = ERR

    clean_boot_config(ops_conn)

    return ret

def main(usb_path = ''):
    """The main function of user script. It is called by ZTP frame, so do not remove or change this function.

    Args:
    Raises:
    Returns: user script processing result
    """
    host = "localhost"
    if usb_path and len(usb_path):
        logging.info('ztp_script usb_path: %s', usb_path)
        global FILE_SERVER
        FILE_SERVER = 'file:///' + usb_path
    try:
        # Make an OPS connection instance.
        ops_conn = OPSConnection(host)
        ret = main_proc(ops_conn)

    except OPIExecError, reason:
        logging.error('OPI execute error: %s', reason)
        print("Error: %s" % reason)
        ret = ERR

    except BootError, reason:
        print("Error: %s" % reason)
        ret = ERR

    except IOError, reason:
        print("Error: %s" % reason)
        ret = ERR

    except Exception, reason:
        logging.error(reason)
        ret = ERR
        
    except UserAbort:
        print("Info: User abort ZTP and continue with normal startup.")
        ret = ERR

    finally:
        clean_boot_config(ops_conn)
        # Close the OPS connection
        ops_conn.close()

    return ret

if __name__ == "__main__":
    main()
