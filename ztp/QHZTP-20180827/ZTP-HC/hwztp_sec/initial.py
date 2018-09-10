#md5sum=""
#!/usr/bin/env python
#
# Copyright (C) Huawei Technologies Co., Ltd. 2008-2013. All rights reserved.
# ----------------------------------------------------------------------------------------------------------------------
# History:
# Date                Author                      Modification
# 20180101            Author                      created file.
# ----------------------------------------------------------------------------------------------------------------------

"""
Zero Touch Provisioning (ZTP) enables devices to automatically load version files including system software,
patch files, configuration files when the device starts up, the devices to be configured must be new devices
or have no configuration files.

This is a sample of Zero Touch Provisioning user script. You can customize it to meet the requirements of
your network environment.
"""

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
import ops

from urlparse import urlparse
from urlparse import urlunparse
from time import sleep


# error code
OK          = 0
ERR         = 1

# File server in which stores the necessary system software, configuration and patch files:
#   1) Specify the file server which supports the following format.
#      tftp://hostname
#      ftp://[username[:password]@]hostname[:port]
#      sftp://[username[:password]@]hostname[:port]
#      http://hostname[:port]
#   2) Do not add a trailing slash at the end of file server path.


# Remote file paths:
#   1) The path may include directory name and file name.
#   2) If file name is not specified, indicate the procedure can be skipped.
# File paths of system software on file server, filename extension is '.cc'.
REMOTE_PATH_IMAGE = {
    'CE5850EI'    :   '',
    'CE6875EI'    :   '',
    'CE12800'     :   '',
}
# File path of configuration file on file server, filename extension is '.cfg', '.zip' or '.dat'.
REMOTE_PATH_CONFIG = ''
# File path of patch file on file server, filename extension is '.pat'
REMOTE_PATH_PATCH = {
    'CE5850EI'    :   '',
    'CE6875EI'    :   '',
    'CE12800'     :   '',
}
# File path of stack member ID file on file server, filename extension is '.txt'
REMOTE_PATH_MEMID = ''
# File path of license list file, filename extension is '.xml'
REMOTE_PATH_LICLIST = ''
# File path of md5 file, contains md5 value of image / patch / memid / license file, file extension is '.txt'
REMOTE_PATH_MD5 = ''
# File path of python file on file server, filename extension is '.py'
REMOTE_PATH_PYTHON_ADD_ON = 'ztp_add_on.py'
REMOTE_PATH_PYTHON_DELETE = 'ztp_delete.py'
FILE_SERVER = ''

# Max times to retry get startup when no query result
GET_STARTUP_INTERVAL = 15     # seconds
MAX_TIMES_GET_STARTUP = 120   # Max times to retry

# Max times to retry when download file faild
MAX_TIMES_RETRY_DOWNLOAD = 3
IFTYPE_LIST = ['100GE', '40GE', '25GE', '10GE', 'GEBrief']

LOG_FILE_EXECUTE = 'ztp_initial.log'

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

        logging.info('HTTP request: %s %s HTTP/1.1', method, uri)
        self.conn.request(method, uri, body, self.headers)
        response = self.conn.getresponse()
        ret = (response.status, response.reason, response.read())
        if response.status != httplib.OK:
            logging.info('%s', body)
            logging.error('HTTP response: HTTP/1.1 %s %s\n%s', ret[0], ret[1], ret[2])
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

def read_csv():
    """This function resolves the CSV file and returns system information, L2 link information, L3 link information"""

    rows1 = []
    rows2 = []
    rows3 = []
    device = {}
    table1 = True
    table2 = False
    table3 = False
    for line in open('Agile-Controller-DCN.csv'):
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

def get_addr_by_hostname(ops_conn, host, addr_type = '1'):
    """Translate a host name to IPv4 address format. The IPv4 address is returned as a string."""

    logging.info("Get IP address by host name...")
    uri = "/dns/dnsNameResolution"
    root_elem = etree.Element('dnsNameResolution')
    etree.SubElement(root_elem, 'host').text = host
    etree.SubElement(root_elem, 'addrType').text = addr_type
    req_data = etree.tostring(root_elem, "UTF-8")
    print "req_data" + req_data
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK:
        raise OPIExecError('Failed to get address by host name')
    print "rsp_data" + rsp_data
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "ipv4Addr", namespaces)
    if elem is None:
        raise OPIExecError('Failed to get IP address by host name')

    return elem.text


def set_same_layer_interface_description(interface_description_map,rows1,rows2):
    sysIndex = rows1['ne index']
    for index in range(1,len(rows2)):
        line_list = rows2[index]
        if line_list[0] ==sysIndex and line_list[6]=='':
            local_interface_name = line_list[0].strip()
            local_interface_port = line_list[1].strip()
            local_eth_trunk_port = line_list[2]
            remote_interface_name = line_list[3].strip()
            remote_interface_port = line_list[4].strip()
            remote_eth_trunk_port = line_list[5]
            if(local_eth_trunk_port!=None and isinstance(local_eth_trunk_port,str) and local_eth_trunk_port.strip()!=''):
                key = '%s-%s'%(local_eth_trunk_port.split('-')[0].capitalize(),local_eth_trunk_port.split('-')[1].capitalize())
                value = 'To_%s_%s'%(remote_interface_name,remote_eth_trunk_port)
                interface_description_map[key] = value
            key = local_interface_port
            value = 'To_%s_%s'%(remote_interface_name,remote_interface_port)
            interface_description_map[key] = value
        elif line_list[3]==sysIndex and line_list[6]=='':
            remote_interface_name = line_list[0].strip()
            remote_interface_port = line_list[1].strip()
            remote_eth_trunk_port = line_list[2]
            local_interface_name = line_list[3].strip()
            local_interface_port = line_list[4].strip()
            local_eth_trunk_port = line_list[5]
            if(local_eth_trunk_port!=None and isinstance(local_eth_trunk_port,str) and local_eth_trunk_port.strip()!=''):
                key = '%s-%s'%(local_eth_trunk_port.split('-')[0].capitalize(),local_eth_trunk_port.split('-')[1].capitalize())
                value = 'To_%s_%s'%(remote_interface_name,remote_eth_trunk_port)
                interface_description_map[key] = value
            key = local_interface_port
            value = 'To_%s_%s'%(remote_interface_name,remote_interface_port)
            interface_description_map[key] = value

def set_divide_layer_interface_description(interface_description_map,rows1,rows3):
    sysIndex = rows1['ne index']
    for index in range(1,len(rows3)):
        line_list = rows3[index]
        if line_list[0] ==sysIndex:
            local_interface_name = line_list[0].strip()
            local_interface_port = line_list[1].strip()
            local_connect_ip = line_list[2]
            remote_interface_name = line_list[4].strip()
            remote_interface_port = line_list[5].strip()
            remote_connect_ip = line_list[6]
            key = local_interface_port
            value = 'To_%s_%s_%s'%(remote_interface_name,remote_connect_ip.split('/')[0],remote_interface_port)
            interface_description_map[key] = value
        elif line_list[4]==sysIndex:
            remote_interface_name = line_list[0].strip()
            remote_interface_port = line_list[1].strip()
            remote_connect_ip = line_list[2]
            local_interface_name = line_list[4].strip()
            local_interface_port = line_list[5].strip()
            local_connect_ip = line_list[6]
            key = local_interface_port
            value = 'To_%s_%s_%s'%(remote_interface_name,remote_connect_ip.split('/')[0],remote_interface_port)
            interface_description_map[key] = value

def set_leaf_bgp_underlay_description(bgp_info_map,bgp_item1):
    ipAddress = bgp_item1['remote_ip'].split('/')[0]
    description ='%s %s %s'%(ipAddress,'description',bgp_item1['remote_sysname'])
    key = '%s_%s'%('Underlay',bgp_item1['remote_port'])
    value = description
    bgp_info_map[key] = value

def set_leaf_bgp_overlay_description(bgp_info_map,bgp_item1):
    ipAddress = bgp_item1['remote_loopback']
    description ='%s %s %s'%(ipAddress,'description',bgp_item1['remote_sysname'])
    key = '%s_%s'%('Overlay',bgp_item1['remote_port'])
    value = description
    bgp_info_map[key] = value

def set_leaf_bgp_description(bgp_info_map, bgp_item1):
    set_leaf_bgp_underlay_description(bgp_info_map, bgp_item1)
    set_leaf_bgp_overlay_description(bgp_info_map,bgp_item1)

def set_leaf_bgp_info(bgp_info_map, rows1, rows2, rows3):
    bgp_peer_list = []
    sysIndex = rows1['ne index']
    for index in range(1,len(rows2)):
        line_list = rows2[index]
        if line_list[0] ==sysIndex and line_list[6]!='':
            local_interface_name = line_list[0].strip()
            local_interface_port = line_list[1].strip()
            local_eth_trunk_port = line_list[2]
            remote_interface_name = line_list[3].strip()
            remote_interface_port = line_list[4].strip()
            remote_eth_trunk_port = line_list[5]
            item = dict(local_sysname=local_interface_name,local_port =local_interface_port,remote_sysname=remote_interface_name,remote_port = remote_interface_port,remote_ip = '',remote_loopback='')
            bgp_peer_list.append(item)
        elif line_list[3]==sysIndex and line_list[6]!='':
            remote_interface_name = line_list[0].strip()
            remote_interface_port = line_list[1].strip()
            remote_eth_trunk_port = line_list[2]
            local_interface_name = line_list[3].strip()
            local_interface_port = line_list[4].strip()
            local_eth_trunk_port = line_list[5]
            item = dict(local_sysname=local_interface_name,local_port =local_interface_port,remote_sysname=remote_interface_name,remote_port = remote_interface_port,remote_ip = '',remote_loopback='')
            bgp_peer_list.append(item)
    for bgp_item in bgp_peer_list:
        for index in range(1,len(rows3)):
            row3_line = rows3[index]
            if row3_line[0] ==bgp_item['remote_sysname']:
                remote_ip = row3_line[2]
                remote_loopback = row3_line[9].split('/')[0]
                bgp_item['remote_ip'] = remote_ip
                bgp_item['remote_loopback'] = remote_loopback
            elif row3_line[4]==bgp_item['remote_sysname']:
                remote_ip = row3_line[6]
                remote_loopback = row3_line[9].split('/')[0]
                bgp_item['remote_ip'] = remote_ip
                bgp_item['remote_loopback'] = remote_loopback
    for bgp_item1 in bgp_peer_list:
        set_leaf_bgp_description(bgp_info_map,bgp_item1)

def set_interface_description(rows1,rows2,rows3):
    bgp_info_map = {}
    interface_description_map={}
    # print('Start to set the device interface description which in same layer')
    logging.info('Start to set the device interface description which in same layer')
    set_same_layer_interface_description(interface_description_map,rows1,rows2)
    Role = rows1["device role"].lower()
    if Role == 'leaf':
        # print('Start to set the leaf device divide layer interface description')
        logging.info('Start to set the leaf device divide layer interface description')
        set_divide_layer_interface_description(interface_description_map,rows1,rows3)
        # print('Start to set the leaf device bgp info')
        logging.info('Start to set the leaf device bgp info')
        set_leaf_bgp_info(bgp_info_map,rows1,rows2,rows3)
    return interface_description_map,bgp_info_map

def _http_download_file(ops_conn, url, local_path):
    """Download file using HTTP."""
    logging.info('HTTP download "%s" to "%s".', url, local_path)

    url_tuple = urlparse(url)
    if not re.match(r"\d+\.\d+\.\d+\.\d+", url_tuple.hostname):
        netloc = get_addr_by_hostname(ops_conn, url_tuple.hostname)
        if url_tuple.port:
            netloc += ':' + str(url_tuple.port)
        url = urlunparse((url_tuple.scheme, netloc, url_tuple.path, url_tuple.params, url_tuple.query,
                          url_tuple.fragment))

    ret = OK
    opener = urllib.URLopener()
    try:
        dst_file_path = "%s/%s" % (os.getcwd(), os.path.basename(url))
        dst_file_path = os.path.abspath(dst_file_path)
        logging.info('HTTP download destination file=%s.', dst_file_path)
        opener.retrieve(url, dst_file_path)
        os.chmod(dst_file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    except (KeyboardInterrupt, Exception), reason:
        if os.path.exists(dst_file_path):
            os.remove(dst_file_path)    # Remove incomplete file
        logging.error(reason)
        print('Error: Failed to download file "%s" using HTTP' % os.path.basename(url))
        ret = ERR

    return ret

def _ftp_download_file(ops_conn, url, local_path):
    """Download file using FTP."""
    logging.info('FTP download "%s" to "%s".', url, local_path)
    uri = "/ftpc/ftpcTransferFiles/ftpcTransferFile"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<ftpcTransferFile>
    <serverIpv4Address>$serverIp</serverIpv4Address>
    <commandType>get</commandType>
    <userName>$username</userName>
    <password>$password</password>
    <localFileName>$localPath</localFileName>
    <remoteFileName>$remotePath</remoteFileName>
</ftpcTransferFile>
''')
    url_tuple = urlparse(url)
    if re.match(r"\d+\.\d+\.\d+\.\d+", url_tuple.hostname):
        server_ip = url_tuple.hostname
    else:
        server_ip = get_addr_by_hostname(ops_conn, url_tuple.hostname)
    req_data = str_temp.substitute(serverIp = server_ip, username = url_tuple.username, password = url_tuple.password,
                                   remotePath = url_tuple.path[1:], localPath = local_path)
    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        print('Failed to download file "%s" using FTP' % os.path.basename(local_path))
        return ERR

    return OK

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

def _del_sshc_rsa_key(ops_conn, server_name, key_type = 'RSA'):
    """Delete SSH client RSA key configuration"""
    logging.debug("Delete SSH client RSA key for %s", server_name)
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

def _sftp_download_file(ops_conn, url, local_path):
    """Download file using SFTP."""
    _set_sshc_first_time(ops_conn, 'Enable')

    logging.info('SFTP download "%s" to "%s".', url, local_path)
    uri = "/sshc/sshcConnects/sshcConnect"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<sshcConnect>
    <HostAddrIPv4>$serverIp</HostAddrIPv4>
    <serverPort>$serverPort</serverPort>
    <commandType>get</commandType>
    <userName>$username</userName>
    <password>$password</password>
    <localFileName>$localPath</localFileName>
    <remoteFileName>$remotePath</remoteFileName>
    <identityKey>ssh-rsa</identityKey>
    <transferType>SFTP</transferType>
</sshcConnect>
''')
    url_tuple = urlparse(url)
    if re.match(r"\d+\.\d+\.\d+\.\d+", url_tuple.hostname):
        server_ip = url_tuple.hostname
    else:
        server_ip = get_addr_by_hostname(ops_conn, url_tuple.hostname)
    req_data = str_temp.substitute(serverIp = server_ip, serverPort = url_tuple.port, username = url_tuple.username, password = url_tuple.password,
                                   remotePath = url_tuple.path[1:], localPath = local_path)
    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        print('Failed to download file "%s" using SFTP' % os.path.basename(local_path))
        ret = ERR
    else:
        ret = OK

    _del_sshc_rsa_key(ops_conn, server_ip)
    _set_sshc_first_time(ops_conn, 'Disable')
    return ret

def _tftp_download_file(ops_conn, url, local_path):
    """Download file using TFTP."""
    logging.info('TFTP download "%s" to "%s".', url, local_path)
    uri = "/tftpc/tftpcTransferFiles/tftpcTransferFile"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<tftpcTransferFile>
    <serverIpv4Address>$serverIp</serverIpv4Address>
    <commandType>get_cmd</commandType>
    <localFileName>$localPath</localFileName>
    <remoteFileName>$remotePath</remoteFileName>
</tftpcTransferFile>
''')
    url_tuple = urlparse(url)
    if re.match(r"\d+\.\d+\.\d+\.\d+", url_tuple.hostname):
        server_ip = url_tuple.hostname
    else:
        server_ip = get_addr_by_hostname(ops_conn, url_tuple.hostname)
    req_data = str_temp.substitute(serverIp = server_ip, remotePath = url_tuple.path[1:], localPath = local_path)
    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        print('Failed to download file "%s" using TFTP' % os.path.basename(local_path))
        return ERR

    return OK

def _usb_download_file(ops_conn, url, local_path):
    """Download file using usb"""
    logging.info('USB download "%s" to "%s".', url, local_path)

    url_tuple = urlparse(url, allow_fragments=False)
    src_path = url_tuple.path[1:]
    try:
        copy_file(ops_conn, src_path, local_path)
    except:
        print('Failed to download file "%s" using USB' % os.path.basename(local_path))
        return ERR
    return OK

def download_file(ops_conn, url, local_path, retry_times = 0):
    """Download file, support TFTP, FTP, SFTP and HTTP.

    tftp://hostname/path
    ftp://[username[:password]@]hostname[:port]/path
    sftp://[username[:password]@]hostname[:port]/path
    http://hostname[:port]/path

    Args:
      ops_conn: OPS connection instance
      url: URL of remote file
      local_path: local path to put the file

    Returns:
        A integer of return code
    """
    url_tuple = urlparse(url)
    print("Info: Download %s to %s" % (url_tuple.path[1:], local_path))
    func_dict = {'tftp': _tftp_download_file,
                 'ftp':  _ftp_download_file,
                 'sftp': _sftp_download_file,
                 'http': _http_download_file,
                 'file': _usb_download_file}
    scheme = url_tuple.scheme
    if scheme not in func_dict.keys():
        raise ZTPErr('Unknown file transfer scheme %s' % scheme)

    ret = OK
    cnt = 0
    while (cnt < 1 + retry_times):
        if cnt:
            print('Retry downloading...')
            logging.info('Retry downloading...')
        ret = func_dict[scheme](ops_conn, url, local_path)
        if ret is OK:
            break
        cnt += 1

    if ret is not OK:
        raise ZTPErr('Failed to download file "%s"' % os.path.basename(url))

    return OK


class StartupInfo(object):
    """Startup configuration information

    image: startup system software
    config: startup saved-configuration file
    patch: startup patch package
    """
    def __init__(self, image = None, config = None, patch = None):
        self.image = image
        self.config = config
        self.patch = patch

class Startup(object):
    """Startup configuration information

    current: current startup configuration
    next: current next startup configuration
    """
    def __init__(self, ops_conn):
        self.ops_conn = ops_conn
        self.current, self.next = self._get_startup_info()

    def _get_startup_info(self):
        """Get the startup information."""
        logging.info("Get the startup information...")
        uri = "/cfg/startupInfos/startupInfo"
        req_data = '''<?xml version="1.0" encoding="UTF-8"?>
<startupInfo>
    <position/>
    <configedSysSoft/>
    <curSysSoft/>
    <nextSysSoft/>
    <curStartupFile/>
    <nextStartupFile/>
    <curPatchFile/>
    <nextPatchFile/>
</startupInfo>'''

        cnt = 0
        while (cnt < MAX_TIMES_GET_STARTUP):
            ret, _, rsp_data = self.ops_conn.get(uri, req_data)
            if ret != httplib.OK or rsp_data is '':
                cnt += 1
                logging.warning('Failed to get the startup information')
                continue

            root_elem = etree.fromstring(rsp_data)
            namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
            mpath = 'data' + uri.replace('/', '/vrp:')  # match path
            nslen = len(namespaces['vrp'])
            elem = root_elem.find(mpath, namespaces)
            if elem is not None:
                break
            logging.warning('No query result while getting startup info')
            sleep(GET_STARTUP_INTERVAL)     # sleep to wait for system ready when no query result
            cnt += 1

        if elem is None:
            raise OPIExecError('Failed to get the startup information')

        current = StartupInfo()     # current startup info
        curnext = StartupInfo()     # next startup info
        for child in elem:
            tag = child.tag[nslen + 2:]       # skip the namespace, '{namespace}text'
            if tag == 'curSysSoft':
                current.image = child.text
            elif tag == 'nextSysSoft':
                curnext.image = child.text
            elif tag == 'curStartupFile' and child.text != 'NULL':
                current.config = child.text
            elif tag == 'nextStartupFile' and child.text != 'NULL':
                curnext.config = child.text
            elif tag == 'curPatchFile' and child.text != 'NULL':
                current.patch = child.text
            elif tag == 'nextPatchFile' and child.text != 'NULL':
                curnext.patch = child.text
            else:
                continue

        return current, curnext

    def _set_startup_image_file(self, file_path):
        """Set the next startup system software"""
        logging.info("Set the next startup system software to %s...", file_path)
        uri = "/sum/startupbymode"
        str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<startupbymode>
    <softwareName>$fileName</softwareName>
    <mode>STARTUP_MODE_ALL</mode>
</startupbymode>
''')
        req_data = str_temp.substitute(fileName = file_path)
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = self.ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError("Failed to set startup system software")

    def _set_startup_config_file(self, file_path):
        """Set the next startup saved-configuration file"""
        logging.info("Set the next startup saved-configuration file to %s...", file_path)
        uri = "/cfg/setStartup"
        str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<setStartup>
    <fileName>$fileName</fileName>
</setStartup>
''')
        req_data = str_temp.substitute(fileName = file_path)
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = self.ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError("Failed to set startup configuration file")

    def _del_startup_config_file(self):
        """Delete startup config file"""
        logging.info("Delete the next startup config file...")
        uri = "/cfg/clearStartup"
        req_data = '''<?xml version="1.0" encoding="UTF-8"?>
<clearStartup>
</clearStartup>
'''
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = self.ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError("Failed to delete startup configuration file")

    def _set_startup_patch_file(self, file_path):
        """Set the next startup patch file"""
        logging.info("Set the next startup patch file to %s...", file_path)
        uri = "/patch/startup"
        str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<startup>
    <packageName>$fileName</packageName>
</startup>
''')
        req_data = str_temp.substitute(fileName = file_path)
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = self.ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError("Failed to set startup patch file")

    def _get_cur_stack_member_id(self):
        """rest api: Get current stack member id"""

        logging.info("Get current stack member ID...")
        uri = "/stack/stackMemberInfos/stackMemberInfo"
        req_data =  \
            '''<?xml version="1.0" encoding="UTF-8"?>
            <stackMemberInfo>
                    <memberID></memberID>
                </stackMemberInfo>
            '''
        ret, _, rsp_data = self.ops_conn.get(uri, req_data)
        if ret != httplib.OK or rsp_data is '':
            raise OPIExecError('Failed to get current stack member id, rsp not ok')

        root_elem = etree.fromstring(rsp_data)
        namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
        uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
        elem = root_elem.find(uri + "memberID", namespaces)
        if elem is None:
            raise OPIExecError('Failed to get the current stack member id for no "memberID" element')

        return elem.text

    def _set_stack_member_id(self, memid):
        """Set the next stack member ID"""
        uri = "/stack/stackMemberInfos/stackMemberInfo"
        str_temp = string.Template(
            '''<?xml version="1.0" encoding="UTF-8"?>
                <stackMemberInfo>
                    <memberID>$curmemberid</memberID>
                    <nextMemberID>$memberid</nextMemberID>
                </stackMemberInfo>
            ''')

        cur_memid = self._get_cur_stack_member_id()
        next_memid = memid

        req_data = str_temp.substitute(curmemberid = cur_memid, memberid = next_memid)
        ret, _, _ = self.ops_conn.set(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to set stack id {}'.format(next_memid))

        return OK

    def _reset_stack_member_id(self):
        """rest api: reset stack member id"""

        logging.info('Reset the next stack member ID')
        uri = "/stack/stackMemberInfos/stackMemberInfo"
        req_data = \
            '''<?xml version="1.0" encoding="UTF-8"?>
                <stackMemberInfo>
                    <memberID>1</memberID>
                    <nextMemberID>1</nextMemberID>
                </stackMemberInfo>
            '''

        ret, _, _ = self.ops_conn.set(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to reset stack id ')

        return OK

    def _reset_startup_patch_file(self):
        """Rest patch file for system to startup"""
        logging.info("Reset the next startup patch file...")
        uri = "/patch/resetpatch"
        req_data = '''<?xml version="1.0" encoding="UTF-8"?>
<resetpatch>
</resetpatch>
'''
        # it is a action operation, so use create for HTTP POST
        ret, _, _ = self.ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            raise OPIExecError('Failed to reset patch')

    def reset_startup_info(self, slave):
        """Reset startup info and delete the downloaded files"""
        logging.info("Reset the next startup information...")
        _, configured = self._get_startup_info()

        # 1. Reset next startup config file and delete it
        try:
            if configured.config != self.next.config:
                if self.next.config is None:
                    self._del_startup_config_file()
                else:
                    self._set_startup_config_file(self.next.config)
                    if configured.config is not None:
                        del_file_all(self.ops_conn, configured.config, slave)

        except Exception, reason:
            logging.error(reason)

        # 2. Reset next startup patch file
        try:
            if configured.patch != self.next.patch:
                if self.next.patch is None:
                    self._reset_startup_patch_file()
                else:
                    self._set_startup_patch_file(self.next.patch)

                if configured.patch is not None:
                    del_file_all(self.ops_conn, configured.patch, slave)
        except Exception, reason:
            logging.error(reason)

        # 3. Reset next startup system software and delete it
        try:
            if configured.image != self.next.image:
                self._set_startup_image_file(self.next.image)
                del_file_all(self.ops_conn, configured.image, slave)
        except Exception, reason:
            logging.error(reason)

        # 4. reset stack member id
        try:
            self._reset_stack_member_id()
        except Exception, reason:
            logging.error(reason)

    def set_startup_info(self, image_file, config_file, patch_file, memid, slave, esn_str):
        """Set the next startup information."""
        logging.info("Set the next startup information...")
        # 1. Set next startup system software
        if image_file is not None:
            try:
                self._set_startup_image_file(image_file)
            except Exception, reason:
                logging.error(reason)
                del_file_all(self.ops_conn, image_file, slave)
                self.reset_startup_info(slave)
                raise

        # 2. Set next startup config file
        if config_file is not None:
            try:
                self._set_startup_config_file(config_file)
            except Exception, reason:
                logging.error(reason)
                del_file_all(self.ops_conn, config_file, slave)
                self.reset_startup_info(slave)
                raise

        # 3. Set next startup patch file
        if patch_file is not None:
            try:
                self._set_startup_patch_file(patch_file)
            except Exception, reason:
                logging.error(reason)
                del_file_all(self.ops_conn, patch_file, slave)
                self.reset_startup_info(slave)
                raise

        # 4. Set next member id
        if memid is not None:
            try:
                self._set_stack_member_id(memid)
            except Exception, reason:
                logging.error(reason)
                self.reset_startup_info(slave)
                raise

def get_cwd(ops_conn):
    """Get the full filename of the current working directory"""
    logging.info("Get the current working directory...")
    uri = "/vfm/pwds/pwd"
    req_data =  \
'''<?xml version="1.0" encoding="UTF-8"?>
<pwd>
    <dictionaryName/>
</pwd>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to get the current working directory')

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    elem = root_elem.find(uri + "dictionaryName", namespaces)
    if elem is None:
        raise OPIExecError('Failed to get the current working directory for no "directoryName" element')

    return elem.text

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

def del_file_all(ops_conn, file_path, slave):
    """Delete a file permanently on all main boards"""
    if file_path:
        del_file(ops_conn, file_path)
        if slave:
            del_file(ops_conn, 'slave#' + file_path)

def copy_file(ops_conn, src_path, dest_path):
    """Copy a file"""
    print('Info: Copy file %s to %s...' % (src_path, dest_path))
    logging.info('Copy file %s to %s...', src_path, dest_path)
    uri = "/vfm/copyFile"
    str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<copyFile>
    <srcFileName>$src</srcFileName>
    <desFileName>$dest</desFileName>
</copyFile>
''')
    req_data = str_temp.substitute(src = src_path, dest = dest_path)

    # it is a action operation, so use create for HTTP POST
    ret, _, _ = ops_conn.create(uri, req_data)
    if ret != httplib.OK:
        raise OPIExecError('Failed to copy "%s" to "%s"' % (src_path, dest_path))

def has_slave_mpu(ops_conn):
    """Whether device has slave MPU, returns a bool value"""
    logging.info("Test whether device has slave MPU...")
    uri = "/devm/phyEntitys"
    req_data =  \
'''<?xml version="1.0" encoding="UTF-8"?>
<phyEntitys>
    <phyEntity>
        <entClass>mpuModule</entClass>
        <entStandbyState/>
        <position/>
    </phyEntity>
</phyEntitys>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to get the device slave information')

    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:') + '/vrp:'
    for entity in root_elem.findall(uri + 'phyEntity', namespaces):
        elem = entity.find("vrp:entStandbyState", namespaces)
        if elem is not None and elem.text == 'slave':
            return True

    return False

def get_system_info(ops_conn):
    """Get system info, returns a dict"""
    logging.info("Get the system information...")
    uri = "/system/systemInfo"
    req_data =  \
'''<?xml version="1.0" encoding="UTF-8"?>
<systemInfo>
    <productName/>
    <esn/>
    <mac/>
</systemInfo>
'''
    ret, _, rsp_data = ops_conn.get(uri, req_data)
    if ret != httplib.OK or rsp_data is '':
        raise OPIExecError('Failed to get the system information')

    sys_info = {}.fromkeys(('productName', 'esn', 'mac'))
    root_elem = etree.fromstring(rsp_data)
    namespaces = {'vrp' : 'http://www.huawei.com/netconf/vrp'}
    uri = 'data' + uri.replace('/', '/vrp:')
    nslen = len(namespaces['vrp'])
    elem = root_elem.find(uri, namespaces)
    if elem is not None:
        for child in elem:
            tag = child.tag[nslen + 2:]       # skip the namespace, '{namespace}esn'
            if tag in sys_info.keys():
                sys_info[tag] = child.text

    return sys_info

def test_file_paths(image, config, patch, stack_memid, md5_file, license_list_file):
    """Test whether argument paths are valid."""
    logging.info("Test whether argument paths are valid...")
    # check image file path
    file_name = os.path.basename(image)
    if file_name is not '' and not file_name.lower().endswith('.cc'):
        print('Error: Invalid filename extension of system software')
        return False

    # check config file path
    file_name = os.path.basename(config)
    file_name = file_name.lower()
    _, ext = os.path.splitext(file_name)
    if file_name is not '' and ext not in ['.cfg', '.zip', '.dat']:
        print('Error: Invalid filename extension of configuration file')
        return False

    # check patch file path
    file_name = os.path.basename(patch)
    if file_name is not '' and not file_name.lower().endswith('.pat'):
        print('Error: Invalid filename extension of patch file')
        return False

    # check stack member id file path
    file_name = os.path.basename(stack_memid)
    if file_name is not '' and not file_name.lower().endswith('.txt'):
        print('Error: Invalid filename extension of stack member ID file')
        return False

    # check md5 file path
    file_name = os.path.basename(md5_file)
    if file_name is not '' and not file_name.lower().endswith('.txt'):
        print('Error: Invalid filename extension of md5 file')
        return False

    # check license list file path
    file_name = os.path.basename(license_list_file)
    if file_name is not '' and not file_name.lower().endswith('.xml'):
        print('Error: Invalid filename extension of license list file')
        return False

    return True

def md5sum(fname, need_skip_first_line = False):
    """
    Calculate md5 num for this file.
    """

    def read_chunks(fhdl):
        '''read chunks'''
        chunk = fhdl.read(8096)
        while chunk:
            yield chunk
            chunk = fhdl.read(8096)
        else:
            fhdl.seek(0)

    md5_obj = hashlib.md5()
    if isinstance(fname, basestring) and os.path.exists(fname):
        with open(fname, "rb") as fhdl:
            #skip the first line
            fhdl.seek(0)
            if need_skip_first_line:
                fhdl.readline()
            for chunk in read_chunks(fhdl):
                md5_obj.update(chunk)
    elif fname.__class__.__name__ in ["StringIO", "StringO"] or isinstance(fname, file):
        for chunk in read_chunks(fname):
            md5_obj.update(chunk)
    else:
        pass
    return md5_obj.hexdigest()

def md5_get_from_file(fname):
    """Get md5 num form file, stored in first line"""

    with open(fname, "rb") as fhdl:
        fhdl.seek(0)
        line_first = fhdl.readline()

    # if not match pattern, the format of this file is not supported
    if not re.match('^#md5sum="[\\w]{32}"[\r\n]+$', line_first):
        return 'None'

    return line_first[9:41]

def md5_check_with_first_line(fname):
    """Validate md5 for this file"""

    fname = os.path.basename(fname)
    md5_calc = md5sum(fname, True)
    md5_file = md5_get_from_file(fname)

    if md5_file.lower() != md5_calc:
        logging.warning('MD5 check failed, file %s', fname)
        print('MD5 checksum of the file "%s" is %s' % (fname, md5_calc))
        logging.warning('MD5 checksum of the file "%s" is %s', fname, md5_calc)
        print('MD5 checksum received from the file "%s" is %s' % (fname, md5_file))
        logging.warning('MD5 checksum received from the file "%s" is %s', fname, md5_file)
        return False

    return True

def md5_check_with_dic(md5_dic, fname):
    """md5 check with dic"""
    if not md5_dic.has_key(fname):
        logging.info('md5_dic does not has key %s, no need to do md5 verification', fname)
        return True

    md5sum_result = md5sum(fname, False)
    if md5_dic[fname] == md5sum_result:
        return True

    print('MD5 checksum of the file "%s" is %s' % (fname, md5sum_result))
    print('MD5 checksum received for the file "%s" is %s' % (fname, md5_dic[fname]))
    logging.warning('MD5 check failed, file %s', fname)
    logging.warning('MD5 checksum of the file "%s" is %s', fname, md5sum_result)
    logging.warning('MD5 checksum received for the file "%s" is %s', fname, md5_dic[fname])

    return False

def parse_md5_file(fname):
    """parse md5 file"""

    def read_line(fhdl):
        """read a line by loop"""
        line = fhdl.readline()
        while line:
            yield line
            line = fhdl.readline()
        else:
            fhdl.seek(0)

    md5_dic = {}
    with open(fname, "rb") as fhdl:
        for line in read_line(fhdl):
            line_spilt = line.split()
            if 2 != len(line_spilt):
                continue
            dic_tmp = {line_spilt[0]: line_spilt[1]}
            md5_dic.update(dic_tmp)
    return md5_dic

def verify_and_parse_md5_file(fname):
    """
    vefiry data integrity of md5 file and parse this file

    format of this file is like:
    ------------------------------------------------------------------
    #md5sum="517cf194e2e1960429c6aedc0e4dba37"

    file-name              md5
    conf_5618642831132.cfg c0ace0f0542950beaacb39cd1c3b5716
    ------------------------------------------------------------------
    """
    if not md5_check_with_first_line(fname):
        return ERR, None
    return OK, parse_md5_file(fname)

def check_parameter(aset):
    seq = ['&', '>', '<', '"', "'"]
    if aset:
        for c in seq:
             if c in aset:
                    return True
    return False

def check_filename(ops_conn):
    sys_info = get_system_info(ops_conn)
    url_tuple = urlparse(FILE_SERVER)
    if check_parameter(url_tuple.username) or check_parameter(url_tuple.password):
        raise ZTPErr('Invalid username or password, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_IMAGE.get(sys_info['productName'], ''))
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of system software, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_CONFIG)
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of configuration file, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_PATCH.get(sys_info['productName'], ''))
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of patch file, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_MEMID)
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of member ID file, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_MD5)
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of md5 file, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    file_name = os.path.basename(REMOTE_PATH_LICLIST)
    if file_name is not '' and check_parameter(file_name):
       raise ZTPErr('Invalid filename of license list file, the name should not contain: '+'&'+' >'+' <'+' "'+" '.")
    return OK

def active_license(ops_conn, license_name):
    if license_name:
        uri = "/lcs/lcsActive"
        str_temp = string.Template(
'''<?xml version="1.0" encoding="UTF-8"?>
<lcsActive>
    <lcsFileName>$lcsFileName</lcsFileName>
</lcsActive>
''')
        req_data = str_temp.substitute(lcsFileName = license_name)
        ret, _, rsp_data = ops_conn.create(uri, req_data)
        if ret != httplib.OK:
            if rsp_data.find("has been activated") > -1:
                print ("Info: There is already actived license on the device")
                return 2
            logging.error('Error: Failed to active license.')
            return ERR
    return OK


def set_lldp_enable(ops_conn):

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

def ops_install_file(filename):
    """
    set_dhcp_relay

    @param1 vlanIfNum: this is vlanIf Num
    @param2 dhcpSeverIp: this is dhcp Sever Ip
    @param3 giAddr: this is gate Addr

    """

    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"ops uninstall file " + filename)
    _ops.cli.execute(handle,"ops install file " + filename)
    handle, err_desp = _ops.cli.close(handle)
    return


def get_wildcardmask(intMask):
    """Get wildcard mask based on the mask"""
    mask = ['0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0'
           ,'0', '0', '0', '0', '0', '0', '0', '0']
    for i in range(intMask, 32, 1):
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

def get_port_list(ops_conn, iftype_list):
    """Get a list of all the interfaces existing on current device"""

    ifnames = []    # all the interface names existing on device

    for iftype in iftype_list:
        namelist = get_interfaces_by_if_type(ops_conn, iftype)
        if len(namelist) > 0:
            ifnames += namelist

    return ifnames

def get_portdelete_array(sourceportArr,L3_configArr,neIndex):
    portDeleteArr = {}
    for port in sourceportArr:
        portDeleteArr[port] = True
        for i in range(len(L3_configArr['ifArray'])):
            if L3_configArr['ifArray'][i] == port and L3_configArr['ifNeArray'][i] == neIndex:
                portDeleteArr[port] = False
    return portDeleteArr


def get_L3_information(rows3):
    """Get L3 link information from CSV file"""

    ifIndexA = 0
    ifIndexB = 0
    ifNeIndexA = 0
    ifNeIndexB = 0
    ipv4IndexA = 0
    ipv4IndexB = 0
    ipv6IndexA = 0
    ipv6IndexB = 0
    ifDescriptionIndexA = 0
    ifDescriptionIndexB = 0
    peerMgntipv4IndexA = 0
    peerMgntipv4IndexB = 0
    peerLpbk1ipv4IndexA = 0
    peerLpbk1ipv4IndexB = 0
    for index in range(len(rows3[0])):
        if rows3[0][index] == "A IF Index":
            ifIndexA = index
        if rows3[0][index] == "B IF Index":
            ifIndexB = index
        if rows3[0][index] == "A NEIndex":
            ifNeIndexA = index
        if rows3[0][index] == "B NE Index":
            ifNeIndexB = index
        if rows3[0][index] == "A ConnIPv4":
            ipv4IndexA = index
        if rows3[0][index] == "B ConnIPv4":
            ipv4IndexB = index
        if rows3[0][index] == "A ConnIPv6":
            ipv6IndexA = index
        if rows3[0][index] == "B ConnIPv6":
            ipv6IndexB = index
        if rows3[0][index] == "A-Port-Desp":
            ifDescriptionIndexA = index
        if rows3[0][index] == "B-Port-Desp":
            ifDescriptionIndexB = index
        if rows3[0][index] == "Peer Device MgntIPV4":
            peerMgntipv4IndexA = index
            peerMgntipv4IndexB = index
        if rows3[0][index] == "Peer Device Loopback1 IPV4":
            peerLpbk1ipv4IndexA = index
            peerLpbk1ipv4IndexB = index

    ifArray = []
    ifNeArray = []
    ipv4Array = []
    ipv6Array = []
    ifDescriptionArr = []
    peerMgntipv4Arr = []
    peerLpbk1ipv4Arr = []

    for item in rows3:
        ifArray.append(item[ifIndexA].replace(' ','').upper())
        ifNeArray.append(item[ifNeIndexA])
        ipv4Array.append(item[ipv4IndexA])
        ipv6Array.append(item[ipv6IndexA])
        ifDescriptionArr.append(item[ifDescriptionIndexA])
        peerMgntipv4Arr.append(item[peerMgntipv4IndexA].split(';')[0])
        peerLpbk1ipv4Arr.append(item[peerLpbk1ipv4IndexA].split(';')[0])

    for item in rows3:
        ifArray.append(item[ifIndexB].replace(' ','').upper())
        ifNeArray.append(item[ifNeIndexB])
        ipv4Array.append(item[ipv4IndexB])
        ipv6Array.append(item[ipv6IndexB])
        ifDescriptionArr.append(item[ifDescriptionIndexB])
        peerMgntipv4Arr.append(item[peerMgntipv4IndexB].split(';')[0])
        peerLpbk1ipv4Arr.append(item[peerLpbk1ipv4IndexB].split(';')[0])

    L3_configArr = {}
    L3_configArr['ifArray'] = ifArray
    L3_configArr['ifNeArray'] = ifNeArray
    L3_configArr['ipv4Array'] = ipv4Array
    L3_configArr['ipv6Array'] = ipv6Array
    L3_configArr['ifDescriptionArr'] = ifDescriptionArr
    L3_configArr['peerMgntipv4Arr'] = peerMgntipv4Arr
    L3_configArr['peerLpbk1ipv4Arr'] = peerLpbk1ipv4Arr

    return L3_configArr

def get_sys_information(rows1, isContain_DFSGroup):
    #band mode
    if rows1['bandmgntmode'] == '':
        raise ZTPErr("bandmgntmode is Null")
    else:
        bandMode = rows1['bandmgntmode']

    oldMethDescription = "<ztp:Meth0/0/0-description>"
    oldLoopback1Description = "<ztp:Loopback1-description>"
    oldMgntInterface = "<ztp:Mgnt-Interface>"
    if "OUT_OF_BAND" in bandMode:
        newMethDescription = "AC-Mgnt"
        if isContain_DFSGroup == True:
            newLoopback1Description = "Router-ID/BGP-Peer-IP/DFS-Group"
        else:
            newLoopback1Description = "Router-ID/BGP-Peer-IP"
        newMgntInterface = "Meth0/0/0"
    elif "IN_BAND" in bandMode:
        newMethDescription = ""
        if isContain_DFSGroup == True:
            newLoopback1Description = "AC-Mgnt/Router-ID/BGP-Peer-IP/DFS-Group"
        else:
            newLoopback1Description = "AC-Mgnt/Router-ID/BGP-Peer-IP"
        newMgntInterface = "LoopBack1"
    else:
        raise ZTPErr("bandmgntmode %s is illegal" % bandMode)

    #as number
    oldAsNum = "<ztp:AS-Num>"
    if rows1['as num'] == '':
        raise ZTPErr("as number is Null")
    else:
        newAsNum = rows1['as num']

    #system name
    oldsysname = "<ztp:Sysname>"
    if rows1['sysname'] == '':
        raise ZTPErr("sysname is Null")
    else:
        newsysname = rows1['sysname']
        
    #location
    oldLocation = "<ztp:Location>"
    newLocation = "Beijing China"
    if rows1['location'] != '':
        newLocation = rows1['location']

    #mgnt ip
    oldMgntIP_And_Mask = '<ztp:MgntIP-and-mask>'
    oldMgntIP_And_Wildcardmask = '<ztp:MgntIP-and-wildcardmask>'
    oldMgntIP_No_Mask = '<ztp:MgntIP>'
    if rows1['mgntipv4'] == '':
        raise ZTPErr("mgntipv4 is Null")
    else:
        newMgntIP_And_Mask = rows1['mgntipv4'].split('/')[0] + ' ' + rows1['mgntipv4'].split('/')[1]
        newMgntIP_And_Wildcardmask = rows1['mgntipv4'].split('/')[0] + ' ' + get_wildcardmask(int(rows1['mgntipv4'].split('/')[1]))
        newMgntIP_No_Mask = rows1['mgntipv4'].split('/')[0]
        
    #mgnt vpn
    oldMgntVPN = '<ztp:MgntVPN>'
    if rows1['mgntvpn'] == '':
        newMgntVPN = ''
    else:
        newMgntVPN = rows1['mgntvpn']

    #vtep ip, mask is 32
    oldvtepIpv4 = "<ztp:VTEP-IPv4>"
    oldvtepIpv4_And_Mask = "<ztp:VtepIP-and-mask>"
    oldvtepIpv4_And_Wildcardmask = "<ztp:VtepIP-and-wildcardmask>"
    if rows1['vtep ipv4'] == '':
        raise ZTPErr("vtep ipv4 is Null")
    else:
        newvtepIpv4 = rows1['vtep ipv4']
        newvtepIpv4_And_Mask = rows1['vtep ipv4'] + ' ' + '32'
        newvtepIpv4_And_Wildcardmask = rows1['vtep ipv4'] + ' ' + get_wildcardmask(32)

    #loopback1 ip
    oldLoopBack1Ipv4_And_Mask = "<ztp:Loopback1-IPv4-and-mask>"
    oldLoopBack1Ipv4_And_Wildcardmask = "<ztp:Loopback1-IPv4-and-wildcardmask>"
    oldLoopBack1Ipv4_No_Mask = "<ztp:Loopback1-IPv4>"
    if "OUT_OF_BAND" in bandMode:
        if rows1['loopback1 ipv4'] == '':
            raise ZTPErr("loopback1 ipv4 is Null")
        else:
            newLoopBack1Ipv4_And_Mask = rows1['loopback1 ipv4'].split('/')[0] + ' ' + '32'
            newLoopBack1Ipv4_And_Wildcardmask = rows1['loopback1 ipv4'].split('/')[0] + ' ' + get_wildcardmask(32)
            newLoopBack1Ipv4_No_Mask = rows1['loopback1 ipv4'].split('/')[0]
    else:
        newLoopBack1Ipv4_And_Mask = newMgntIP_And_Mask
        newLoopBack1Ipv4_And_Wildcardmask = newMgntIP_And_Wildcardmask
        newLoopBack1Ipv4_No_Mask = newMgntIP_No_Mask

    # stack info
    oldStackPriority = "<ztp:Stack-Priority>"
    newStackPriority = ''
    oldStackMemId = "<ztp:Stack-Member-ID>"
    newStackMemId = ''
    oldBackupMgntIP_And_Mask = "<ztp:Backup-MgntIP-and-mask>"
    newBackupMgntIP_And_Mask = ''
    if rows1['stack'] != '':
        if rows1['member id'] not in ['1', '2']:
            logging.error('Current mode is stack but member id is not 1 or 2')
            raise ZTPErr("Current mode is stack but member id is not 1 or 2")
        else:
            newStackMemId = rows1['member id']
        if rows1['priority'] == '':
            logging.error('Current mode is stack but priority is null')
            raise ZTPErr("Current mode is stack but priority is null")
        else:
            newStackPriority = rows1['priority']
        if rows1['backup mgntipv4'] == '':
            logging.error('Current mode is stack but backup mgntipv4 is null')
            raise ZTPErr("Current mode is stack but backup mgntipv4 is null")
        else:
            newBackupMgntIP_And_Mask = rows1['backup mgntipv4'].split('/')[0] + ' ' + rows1['backup mgntipv4'].split('/')[1]

    sysConfArr = {}
    sysConfArr['oldMethDescription']                = oldMethDescription
    sysConfArr['oldLoopback1Description']           = oldLoopback1Description
    sysConfArr['oldMgntInterface']                  = oldMgntInterface
    sysConfArr['oldAsNum']                          = oldAsNum
    sysConfArr['oldsysname']                        = oldsysname
    sysConfArr['oldMgntIP_And_Mask']                = oldMgntIP_And_Mask
    sysConfArr['oldMgntIP_And_Wildcardmask']        = oldMgntIP_And_Wildcardmask
    sysConfArr['oldMgntIP_No_Mask']                 = oldMgntIP_No_Mask
    sysConfArr['oldMgntVPN']                        = oldMgntVPN
    sysConfArr['oldvtepIpv4']                       = oldvtepIpv4
    sysConfArr['oldvtepIpv4_And_Mask']              = oldvtepIpv4_And_Mask
    sysConfArr['oldvtepIpv4_And_Wildcardmask']      = oldvtepIpv4_And_Wildcardmask
    sysConfArr['oldLoopBack1Ipv4_And_Mask']         = oldLoopBack1Ipv4_And_Mask
    sysConfArr['oldLoopBack1Ipv4_And_Wildcardmask'] = oldLoopBack1Ipv4_And_Wildcardmask
    sysConfArr['oldLoopBack1Ipv4_No_Mask']          = oldLoopBack1Ipv4_No_Mask
    sysConfArr['oldStackPriority']                  = oldStackPriority
    sysConfArr['oldStackMemId']                     = oldStackMemId
    sysConfArr['oldBackupMgntIP_And_Mask']          = oldBackupMgntIP_And_Mask
    sysConfArr['oldLocation']                       = oldLocation
    sysConfArr['newMethDescription']                = newMethDescription
    sysConfArr['newLoopback1Description']           = newLoopback1Description
    sysConfArr['newMgntInterface']                  = newMgntInterface
    sysConfArr['newAsNum']                          = newAsNum
    sysConfArr['newsysname']                        = newsysname
    sysConfArr['newMgntIP_And_Mask']                = newMgntIP_And_Mask
    sysConfArr['newMgntIP_And_Wildcardmask']        = newMgntIP_And_Wildcardmask
    sysConfArr['newMgntIP_No_Mask']                 = newMgntIP_No_Mask
    sysConfArr['newMgntVPN']                        = newMgntVPN
    sysConfArr['newvtepIpv4']                       = newvtepIpv4
    sysConfArr['newvtepIpv4_And_Mask']              = newvtepIpv4_And_Mask
    sysConfArr['newvtepIpv4_And_Wildcardmask']      = newvtepIpv4_And_Wildcardmask
    sysConfArr['newLoopBack1Ipv4_And_Mask']         = newLoopBack1Ipv4_And_Mask
    sysConfArr['newLoopBack1Ipv4_And_Wildcardmask'] = newLoopBack1Ipv4_And_Wildcardmask
    sysConfArr['newLoopBack1Ipv4_No_Mask']          = newLoopBack1Ipv4_No_Mask
    sysConfArr['newStackPriority']                  = newStackPriority
    sysConfArr['newStackMemId']                     = newStackMemId
    sysConfArr['newBackupMgntIP_And_Mask']          = newBackupMgntIP_And_Mask
    sysConfArr['newLocation']                       = newLocation

    return sysConfArr


def del_redundant_conf(line,rows1, isDeleteOutbandMethConfig, isDeleteOutbandVpnConfig, isDeleteInbandConfig,isSpineRRConfig):
    """
    Partial configuration needs to be removed according to Out-of-band or in-band
    """

    OutbandMethConfigBegin    = "<ztp:OUT_OF_BAND_METH>"
    OutbandMethConfigEnd      = "</ztp:OUT_OF_BAND_METH>"
    OutbandVpnConfigBegin    = "<ztp:OUT_OF_BAND_VPN>"
    OutbandVpnConfigEnd      = "</ztp:OUT_OF_BAND_VPN>"
    InbandConfigBegin     = "<ztp:IN_BAND>"
    InbandConfigEnd       = "</ztp:IN_BAND>"
    IsSpineRRBegin = '<ztp:IS_SPINE_RR>'
    IsSpineRREnd = '</ztp:IS_SPINE_RR>'

    writeline = line

    if OutbandMethConfigBegin in line:
        writeline = ''
        if "OUT_OF_BAND_METH" not in rows1['bandmgntmode']:
            isDeleteOutbandMethConfig = True
            
    if OutbandVpnConfigBegin in line:
        writeline = ''
        if "OUT_OF_BAND_VPN" not in rows1['bandmgntmode']:
            isDeleteOutbandVpnConfig = True

    if InbandConfigBegin in line:
        writeline = ''
        if "IN_BAND" not in rows1['bandmgntmode']:
            isDeleteInbandConfig = True

    if IsSpineRRBegin in line:
        writeline = ''
        if 'rr' not in rows1["device role"].lower():
            isSpineRRConfig = True

    if OutbandMethConfigEnd in line:
        writeline = ''
        isDeleteOutbandMethConfig = False

    if OutbandVpnConfigEnd in line:
        writeline = ''
        isDeleteOutbandVpnConfig = False
        
    if InbandConfigEnd in line:
        writeline = ''
        isDeleteInbandConfig = False

    if IsSpineRREnd in line:
        writeline = ''
        isSpineRRConfig = False

    if isDeleteOutbandMethConfig == True or isDeleteOutbandVpnConfig == True or isDeleteInbandConfig == True or isSpineRRConfig ==True:
        writeline = ''

    return writeline, isDeleteOutbandMethConfig, isDeleteOutbandVpnConfig, isDeleteInbandConfig,isSpineRRConfig


def replace_sys_conf(writeline, sysConfArr):
    """
    Replace system-level configuration
    """

    #replace sysName
    if sysConfArr['oldsysname'] in writeline:
        writeline = writeline.replace(sysConfArr['oldsysname'], sysConfArr['newsysname'])

    #replace as number
    if sysConfArr['oldAsNum'] in writeline:
        writeline = writeline.replace(sysConfArr['oldAsNum'], sysConfArr['newAsNum'])

    #replace meth description
    if sysConfArr['oldMethDescription'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMethDescription'], sysConfArr['newMethDescription'])

    #replace MgntIP
    if sysConfArr['oldMgntIP_And_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMgntIP_And_Mask'], sysConfArr['newMgntIP_And_Mask'])

    if sysConfArr['oldMgntIP_And_Wildcardmask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMgntIP_And_Wildcardmask'], sysConfArr['newMgntIP_And_Wildcardmask'])

    if sysConfArr['oldMgntIP_No_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMgntIP_No_Mask'], sysConfArr['newMgntIP_No_Mask'])

    #replace mgnt interface
    if sysConfArr['oldMgntInterface'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMgntInterface'], sysConfArr['newMgntInterface'])
        
    #replace mgnt vpn
    if sysConfArr['oldMgntVPN'] in writeline:
        writeline = writeline.replace(sysConfArr['oldMgntVPN'], sysConfArr['newMgntVPN'])

    #replace vtep ip
    if sysConfArr['oldvtepIpv4'] in writeline:
        writeline = writeline.replace(sysConfArr['oldvtepIpv4'], sysConfArr['newvtepIpv4'])

    if sysConfArr['oldvtepIpv4_And_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldvtepIpv4_And_Mask'], sysConfArr['newvtepIpv4_And_Mask'])

    if sysConfArr['oldvtepIpv4_And_Wildcardmask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldvtepIpv4_And_Wildcardmask'], sysConfArr['newvtepIpv4_And_Wildcardmask'])

    #replace LoopBack1
    if sysConfArr['oldLoopback1Description'] in writeline:
        writeline = writeline.replace(sysConfArr['oldLoopback1Description'], sysConfArr['newLoopback1Description'])

    if sysConfArr['oldLoopBack1Ipv4_And_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldLoopBack1Ipv4_And_Mask'], sysConfArr['newLoopBack1Ipv4_And_Mask'])

    if sysConfArr['oldLoopBack1Ipv4_No_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldLoopBack1Ipv4_No_Mask'], sysConfArr['newLoopBack1Ipv4_No_Mask'])

    if sysConfArr['oldLoopBack1Ipv4_And_Wildcardmask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldLoopBack1Ipv4_And_Wildcardmask'], sysConfArr['newLoopBack1Ipv4_And_Wildcardmask'])

    #replace stack config
    if sysConfArr['oldStackPriority'] in writeline:
        writeline = writeline.replace(sysConfArr['oldStackPriority'], sysConfArr['newStackPriority'])

    if sysConfArr['oldStackMemId'] in writeline:
        writeline = writeline.replace(sysConfArr['oldStackMemId'], sysConfArr['newStackMemId'])

    if sysConfArr['oldBackupMgntIP_And_Mask'] in writeline:
        writeline = writeline.replace(sysConfArr['oldBackupMgntIP_And_Mask'], sysConfArr['newBackupMgntIP_And_Mask'])
        
    #replace location
    if sysConfArr['oldLocation'] in writeline:
        writeline = writeline.replace(sysConfArr['oldLocation'], sysConfArr['newLocation'])

    return writeline


def replace_l3_conf(writeline, ifnames, lsPortDeleteArr, L3_configArr, rows1):
    """
    Replace L3 configuration
    """

    if L3_configArr == {}:
        return writeline

    for port in ifnames:
        connIPv4_And_Mask = "<ztp L3:" + port + "-ipv4-address-and-mask>"
        connIPv4_And_wildcardmask = "<ztp L3:" + port + "-ipv4-address-and-wildcardmask>"
        twinPort = port.replace("GE1", "GE2")
        twin_ConnIPv4_And_Mask = "<ztp L3:" + twinPort + "-ipv4-address-and-mask>"
        twin_ConnIPv4_And_wildcardmask = "<ztp L3:" + twinPort + "-ipv4-address-and-wildcardmask>"
        portDescription = "<ztp L3:" + port + "-description>"
        neighbor_lpbk1ip = "<ztp:"+ port + "-Neighbor-Loopback1-IPv4>"
        neighbor_connIPv4 = "<ztp L3:"+ port + "-neighbor-ipv4-address>"
        if connIPv4_And_Mask in writeline or connIPv4_And_wildcardmask in writeline or neighbor_lpbk1ip in writeline or twin_ConnIPv4_And_Mask in writeline or twin_ConnIPv4_And_wildcardmask in writeline or neighbor_connIPv4 in writeline :
            if lsPortDeleteArr[port] == True:
                writeline = ''
            else:
                for i in range(len(L3_configArr['ifArray'])):
                    if L3_configArr['ifArray'][i] == port and L3_configArr['ifNeArray'][i] == rows1["ne index"]:
                        if rows1['stack'] == '':
                            newconnIPv4_And_Mask =  L3_configArr['ipv4Array'][i].split('/')[0] + ' ' + L3_configArr['ipv4Array'][i].split('/')[1]
                            newconnIPv4_And_wildcardmask = L3_configArr['ipv4Array'][i].split('/')[0] + ' ' + get_wildcardmask(int(L3_configArr['ipv4Array'][i].split('/')[1]))
                            newportDescription = L3_configArr['ifDescriptionArr'][i]
                            writeline = writeline.replace(connIPv4_And_Mask,newconnIPv4_And_Mask)
                            writeline = writeline.replace(connIPv4_And_wildcardmask,newconnIPv4_And_wildcardmask)
                            writeline = writeline.replace(portDescription,newportDescription)
                            if i > len(L3_configArr['ifArray'])/2:
                                newneighbor_connIPv4 = L3_configArr['ipv4Array'][i-len(L3_configArr['ifArray'])/2].split('/')[0]
                            else:
                                newneighbor_connIPv4 = L3_configArr['ipv4Array'][i+len(L3_configArr['ifArray'])/2].split('/')[0]
                            writeline = writeline.replace(neighbor_connIPv4,newneighbor_connIPv4)
                        else:
                            newconnIPv4_And_Mask = L3_configArr['ipv4Array'][i].split(';')[int(rows1['member id'])-1].split('/')[0] + ' ' + L3_configArr['ipv4Array'][i].split(';')[int(rows1['member id'])-1].split('/')[1]
                            newconnIPv4_And_wildcardmask = L3_configArr['ipv4Array'][i].split(';')[int(rows1['member id'])-1].split('/')[0] + ' ' + get_wildcardmask(int(L3_configArr['ipv4Array'][i].split(';')[int(rows1['member id'])-1].split('/')[1]))
                            writeline = writeline.replace(connIPv4_And_Mask,newconnIPv4_And_Mask)
                            writeline = writeline.replace(connIPv4_And_wildcardmask,newconnIPv4_And_wildcardmask)
                            twin_newconnIPv4_And_Mask = L3_configArr['ipv4Array'][i].split(';')[2-int(rows1['member id'])].split('/')[0] + ' ' + L3_configArr['ipv4Array'][i].split(';')[2-int(rows1['member id'])].split('/')[1]
                            twin_newconnIPv4_And_wildcardmask = L3_configArr['ipv4Array'][i].split(';')[2-int(rows1['member id'])].split('/')[0] + ' ' + get_wildcardmask(int(L3_configArr['ipv4Array'][i].split(';')[2-int(rows1['member id'])].split('/')[1]))
                            writeline = writeline.replace(twin_ConnIPv4_And_Mask,twin_newconnIPv4_And_Mask)
                            writeline = writeline.replace(twin_ConnIPv4_And_wildcardmask,twin_newconnIPv4_And_wildcardmask)

                        if i > len(L3_configArr['ifArray'])/2:
                            newneighbor_lpbk1ip = L3_configArr['peerLpbk1ipv4Arr'][i-len(L3_configArr['ifArray'])/2].split('/')[0]
                        else:
                            newneighbor_lpbk1ip = L3_configArr['peerLpbk1ipv4Arr'][i+len(L3_configArr['ifArray'])/2].split('/')[0]
                        writeline = writeline.replace(neighbor_lpbk1ip,newneighbor_lpbk1ip)

    return writeline

def replace_description_conf(interface_description_map,bgp_info_map,writeline):
    interface_star_tag = '<ztp description:'
    stopTag = '-Description>'
    bgp_start_tag = '<ztp:Bgp-Description-'
    if writeline.find(interface_star_tag)!=-1 and writeline.find(stopTag)!=-1:
        # print('interface_description_map before',writeline)
        port = writeline[writeline.find(interface_star_tag)+len(interface_star_tag):writeline.find(stopTag)]
        value = interface_description_map.get(port)
        if value!=None:
            # writeline = ' %s %s\n'%(writeline.split()[0],value)
            writeline = writeline.replace(interface_star_tag+port+stopTag,value)
            # print('interface_description_map after',writeline)
        else:
            writeline = ''
    elif writeline.find(bgp_start_tag)!=-1 and writeline.find(stopTag)!=-1:
        # print('bgp_info_map before',writeline)
        port = writeline[writeline.find(bgp_start_tag)+len(bgp_start_tag):writeline.find(stopTag)]
        value = bgp_info_map.get(port)
        if value!=None:
            # writeline = ' %s %s\n'%(writeline.split()[0],value)
            writeline = writeline.replace(bgp_start_tag+port+stopTag,value)
            # print('bgp_info_map after',writeline)
        else:
            writeline=''
    return writeline



def change_cfg_device_info(ops_conn,file_path,rows1,rows2,rows3):
    """
    Use the information in the CSV file to replace the parameters in the configuration template to get a usable profile
    """




    #To determine if there is DFS group configuration, some port descriptions are distinguished by this
    isContain_DFSGroup = False
    with open(file_path,"r") as f:
        lines = f.readlines()
        for line in lines:
            if "dfs-group" in line:
                isContain_DFSGroup = True
                break

    #set interface description(incluing eth-trunk)
    interface_description_map,bgp_info_map = set_interface_description(rows1,rows2,rows3)

    #Parsing System Configuration
    sysConfArr = get_sys_information(rows1, isContain_DFSGroup)

    neIndex = rows1["ne index"]
    ifnames = get_port_list(ops_conn, IFTYPE_LIST)

    # If has l3 configuration, parse it
    L3_configArr = {}
    lsPortDeleteArr = []
    if rows3 != []:
        L3_configArr = get_L3_information(rows3)
        lsPortDeleteArr = get_portdelete_array(ifnames,L3_configArr,neIndex)

    with open(file_path,"w") as f_w:
        isDeleteOutbandMethConfig = False
        isDeleteOutbandVpnConfig = False
        isDeleteInbandConfig = False
        isSpineRRConfig = False
        for line in lines:
            writeline = line

            #Replace interface description
            writeline = replace_description_conf(interface_description_map,bgp_info_map,writeline)

            #Remove configuration based on Out-of-band or in-band
            writeline, isDeleteOutbandMethConfig, isDeleteOutbandVpnConfig, isDeleteInbandConfig,isSpineRRConfig = del_redundant_conf(writeline,rows1, isDeleteOutbandMethConfig, isDeleteOutbandVpnConfig, isDeleteInbandConfig,isSpineRRConfig)

            #Replace system-level configuration
            writeline = replace_sys_conf(writeline, sysConfArr)

            #Replace L3 configuration
            writeline = replace_l3_conf(writeline, ifnames, lsPortDeleteArr, L3_configArr, rows1)

            f_w.write(writeline)


def change_lower(dict1):
    dict2 = {}
    for key in dict1:
        dict2[key.lower()] = dict1[key]
    return dict2

def set_layer_interface_description(ops_conn,local_port,description):
    # print('local_port = %s , description = %s'%(local_port,description))
    logging.info('local_port = %s , description = %s'%(local_port,description))

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"interface " + local_port)
    _ops.cli.execute(handle,"description " + description)
    _ops.cli.execute(handle,"comm")

    _ops.cli.close(handle)

    return OK


def get_basiccfg_name(rows1):
    basicCfgName = 'basic_spine.cfg'
    Role = rows1["device role"].lower()
    if Role == 'leaf':
        if rows1["stack"] != '':
            basicCfgName = 'basic_leaf_stack.cfg'
        else:
            basicCfgName = 'basic_leaf_single_mlag.cfg'
    return basicCfgName

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

def delete_logfile(ops_conn):

    _ops = ops.ops()
    handle,_ = _ops.cli.open()
    choice = {"Continue": "y", "continue": "y"}
    _ops.cli.execute(handle,"del /u " + LOG_FILE_EXECUTE,choice)
    _ops.cli.close(handle)

    return OK

def main_proc(ops_conn):

    delete_logfile(ops_conn)
    log_init(LOG_FILE_EXECUTE, logging.INFO)

    """Main processing"""
    sys_info = get_system_info(ops_conn)    # Get system info, such as esn and system mac

    ret = set_lldp_enable(ops_conn)

    productName = sys_info['productName']
    cwd = get_cwd(ops_conn)                 # Get the current working directory
    startup = Startup(ops_conn)
    slave = has_slave_mpu(ops_conn)         # Check whether slave MPU board exists or not
    chg_flag = False

    check_filename(ops_conn)


    rows1,rows2,rows3 = read_csv()
    rows1 = change_lower(rows1)

    xftp_user = rows1['xftp server user']
    xftp_password = rows1['xftp server passwd']
    xftp_ip = rows1['xftp server ip']
    xftp_port = rows1['xftp server port']

    FILE_SERVER = 'sftp://' + xftp_user + ':' + xftp_password + '@' + xftp_ip + ':' + xftp_port

    REMOTE_PATH_CONFIG  = get_basiccfg_name(rows1)
    # check remote file paths
    if not test_file_paths(REMOTE_PATH_IMAGE.get(sys_info['productName'], ''), REMOTE_PATH_CONFIG,
                           REMOTE_PATH_PATCH.get(sys_info['productName'], ''), REMOTE_PATH_MEMID, REMOTE_PATH_MD5,
                           REMOTE_PATH_LICLIST):
        return ERR

    # download md5 file first, used to verify data integrity of files which will be downloaded next
    local_path_md5 = None
    file_path = REMOTE_PATH_MD5
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if file_name is not '':
        url = FILE_SERVER + file_path
        local_path_md5 = cwd + file_name
        ret = download_file(ops_conn, url, local_path_md5, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download MD5 file "%s"' % file_name)
            return ERR
        print('Info: Download MD5 file successfully')
        ret, md5_dic = verify_and_parse_md5_file(file_name)
        # delete the file immediately
        del_file_all(ops_conn, local_path_md5, None)
        if ret is ERR:
            print('Error: MD5 check failed, file "%s"' % file_name)
            return ERR
    else:
        md5_dic = {}

    if rows1['isreplace'].lower() == 'no' :
            # download configuration file
        local_path_config = None

        file_path = REMOTE_PATH_CONFIG
        if not file_path.startswith('/'):
            file_path = '/' + file_path
        file_name = os.path.basename(file_path)
        if file_name is not '':
            url = FILE_SERVER + file_path
            local_path_config = cwd + file_name
            ret = download_file(ops_conn, url, local_path_config, MAX_TIMES_RETRY_DOWNLOAD)
            if ret is ERR or not file_exist(ops_conn, file_name):
                print('Error: Failed to download configuration file "%s"' % file_name)
                return ERR
            print('Info: Download configuration file successfully')
            if not md5_check_with_dic(md5_dic, file_name):
                print('Error: MD5 check failed, file "%s"' % file_name)
                del_file_all(ops_conn, local_path_config, slave)
                return ERR
            change_cfg_device_info(ops_conn,REMOTE_PATH_CONFIG,rows1,rows2,rows3)
            if slave:
                copy_file(ops_conn, local_path_config, 'slave#' + local_path_config)
            chg_flag = True

    else:
        local_path_config = None
        replaceCfg = '/' + rows1['mgntipv4'].split('/')[0] + '.cfg'
        file_path = '/backup_configfile' + replaceCfg

        xftp_user = rows1['backup xftp server user']
        xftp_password = rows1['backup xftp server passwd']
        xftp_ip = rows1['backup xftp server ip']
        xftp_port = rows1['backup xftp server port']
        FILE_SERVER = 'sftp://' + xftp_user + ':' + xftp_password + '@' + xftp_ip + ':' + xftp_port
        if not file_path.startswith('/'):
            file_path = '/' + file_path
        file_name = os.path.basename(file_path)
        if file_name is not '':
            url = FILE_SERVER + file_path
            local_path_config = cwd + file_name
            ret = download_file(ops_conn, url, local_path_config, MAX_TIMES_RETRY_DOWNLOAD)
            if ret is ERR or not file_exist(ops_conn, file_name):
                print('Error: Failed to download configuration file "%s"' % file_name)
                return ERR
            print('Info: Download configuration file successfully')
            if not md5_check_with_dic(md5_dic, file_name):
                print('Error: MD5 check failed, file "%s"' % file_name)
                del_file_all(ops_conn, local_path_config, slave)
                return ERR


        del_file(ops_conn, REMOTE_PATH_CONFIG)
        copy_file(ops_conn, local_path_config, cwd + REMOTE_PATH_CONFIG)
        local_path_config = cwd + REMOTE_PATH_CONFIG

        if slave:
              copy_file(ops_conn, local_path_config, 'slave#' + local_path_config)
        chg_flag = True
        del_file(ops_conn, replaceCfg)



    xftp_user = rows1['xftp server user']
    xftp_password = rows1['xftp server passwd']
    xftp_ip = rows1['xftp server ip']
    xftp_port = rows1['xftp server port']
    FILE_SERVER = 'sftp://' + xftp_user + ':' + xftp_password + '@' + xftp_ip + ':' + xftp_port

    # download patch file
    local_path_patch = None
    file_path = REMOTE_PATH_PATCH.get(sys_info['productName'], '')
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if startup.current.patch:
        cur_pat = os.path.basename(startup.current.patch).lower()
    else:
        cur_pat = ''
    if file_name is not '' and file_name.lower() != cur_pat:
        url  = FILE_SERVER + file_path
        local_path_patch = cwd + file_name
        ret = download_file(ops_conn, url, local_path_patch, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download patch file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            return ERR
        print('Info: Download patch file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            return ERR
        if slave:
            copy_file(ops_conn, local_path_patch, 'slave#' + local_path_patch)
        chg_flag = True

    # download stack member ID file
    local_path_memid = None
    file_path = REMOTE_PATH_MEMID
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if file_name is not '':
        url = FILE_SERVER + file_path
        local_path_memid = cwd + file_name
        ret = download_file(ops_conn, url, local_path_memid, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download system software "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            return ERR
        print('Info: Download stack member ID file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            return ERR
        chg_flag = True
        #no need copy to slave board

    # download system software
    local_path_image = None
    file_path = REMOTE_PATH_IMAGE.get(sys_info['productName'], '')
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if startup.current.image:
        cur_image = os.path.basename(startup.current.image).lower()
    else:
        cur_image = ''
    if file_name is not '' and file_name.lower() != cur_image:
        url  = FILE_SERVER + file_path
        local_path_image = cwd + file_name
        ret = download_file(ops_conn, url, local_path_image, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download system software "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            if file_exist(ops_conn, file_name):
                del_file_all(ops_conn, local_path_image, slave)
            return ERR
        print('Info: Download system software file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            return ERR
        if slave:
            copy_file(ops_conn, local_path_image, 'slave#' + local_path_image)
        chg_flag = True

    # download license list file
    local_path_liclist = None
    file_path = REMOTE_PATH_LICLIST
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    download_space = os.path.dirname(file_path)
    if file_name is not '':
        url = FILE_SERVER + file_path
        local_path_liclist = cwd + file_name
        ret = download_file(ops_conn, url, local_path_liclist, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download license list file "%s"' % file_name)
            return ERR
        print('Info: Download license list file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            return ERR
        chg_flag = True

    #execute license list file to get license file name which end with .dat
    license_name = None
    if local_path_liclist is not None:
        tree = etree.parse(file_name)
        root = tree.getroot()
        for child in root.findall('Lic'):
            name = child.get('name')
            esn = child.find('Esn').text
            if sys_info['esn'] in esn:
                license_name = name
                print('Info: License file name is "%s"' % license_name)
                break
        if license_name == None :
            print('Error: Esn of this device is not in the license list file')
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            return ERR

    # download license file
    local_path_license = None
    file_path = license_name
    if file_path is not None:
        file_path = download_space + file_path
        file_name = os.path.basename(file_path)
        if file_name is not '':
            url  = FILE_SERVER + file_path
            local_path_license = cwd + file_name
            ret = download_file(ops_conn, url, local_path_license, MAX_TIMES_RETRY_DOWNLOAD)
            if ret is ERR or not file_exist(ops_conn, file_name):
                print('Error: Failed to download license file "%s"' % file_name)
                del_file_all(ops_conn, local_path_config, slave)
                del_file_all(ops_conn, local_path_patch, slave)
                del_file_all(ops_conn, local_path_memid, slave)
                del_file_all(ops_conn, local_path_image, slave)
                del_file_all(ops_conn, local_path_liclist, slave)
                return ERR
            print('Info: Download license file successfully')
            if not md5_check_with_dic(md5_dic, file_name):
                print('Error: MD5 check failed, file "%s"' % file_name)
                del_file_all(ops_conn, local_path_config, slave)
                del_file_all(ops_conn, local_path_patch, slave)
                del_file_all(ops_conn, local_path_memid, slave)
                del_file_all(ops_conn, local_path_image, slave)
                del_file_all(ops_conn, local_path_liclist, slave)
                del_file_all(ops_conn, local_path_license, slave)
                return ERR
            chg_flag = True
            #no need copy to slave board

    # download python file
    local_path_python = None
    file_path = REMOTE_PATH_PYTHON_ADD_ON
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if file_name is not '':
        url = FILE_SERVER + file_path
        local_path_python = cwd + file_name
        ret = download_file(ops_conn, url, local_path_python, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download python file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            del_file_all(ops_conn, local_path_license, slave)
            return ERR
        print('Info: Download python file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            del_file_all(ops_conn, local_path_license, slave)
            del_file_all(ops_conn, local_path_python, slave)
            return ERR
        if slave:
            copy_file(ops_conn, local_path_python, 'slave#' + local_path_python)
        chg_flag = True

    if chg_flag is False:
        return ERR

    # download python file
    local_path_python = None
    file_path = REMOTE_PATH_PYTHON_DELETE
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    file_name = os.path.basename(file_path)
    if file_name is not '':
        url = FILE_SERVER + file_path
        local_path_python = cwd + file_name
        ret = download_file(ops_conn, url, local_path_python, MAX_TIMES_RETRY_DOWNLOAD)
        if ret is ERR or not file_exist(ops_conn, file_name):
            print('Error: Failed to download python file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            del_file_all(ops_conn, local_path_license, slave)
            return ERR
        print('Info: Download python file successfully')
        if not md5_check_with_dic(md5_dic, file_name):
            print('Error: MD5 check failed, file "%s"' % file_name)
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            del_file_all(ops_conn, local_path_license, slave)
            del_file_all(ops_conn, local_path_python, slave)
            return ERR
        if slave:
            copy_file(ops_conn, local_path_python, 'slave#' + local_path_python)
        chg_flag = True

    if chg_flag is False:
        return ERR

    ops_install_file("ztp_add_on.py")
    ops_install_file("ztp_delete.py")

    # active license file
    if local_path_license is not None:
        ret = active_license(ops_conn, local_path_license)
        if ret is ERR:
            print('Info: Active license failed')
            del_file_all(ops_conn, local_path_config, slave)
            del_file_all(ops_conn, local_path_patch, slave)
            del_file_all(ops_conn, local_path_memid, slave)
            del_file_all(ops_conn, local_path_image, slave)
            del_file_all(ops_conn, local_path_liclist, slave)
            del_file_all(ops_conn, local_path_license, slave)
            del_file_all(ops_conn, local_path_python, slave)
            return ERR
        if ret is OK:
            print('Info: Active license sucessfully, name: %s' % local_path_license)

    memberid = None
    if rows1['stack'] != '':
        if rows1['member id'] == '':
            print 'Error: Current mode is stack but member id is null'
            logging.error('Current mode is stack but member id is null')
            return ERR
        else:
            memberid = rows1['member id']

    # set startup info
    startup.set_startup_info(local_path_image, local_path_config, local_path_patch,
                             memberid, slave, sys_info['esn'])
    print('Info: set startup configuration successfully')
    # delete stack member ID file and license list file after used
    del_file_all(ops_conn, local_path_memid, None)
    del_file_all(ops_conn, local_path_liclist, None)
    del_file_all(ops_conn, "Agile-Controller-DCN.csv", None)





    return OK

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

    except ZTPErr, reason:
        logging.error('ZTP error: %s', reason)
        print("Error: %s" % reason)
        ret = ERR

    except IOError, reason:
        print("Error: %s" % reason)
        ret = ERR

    except KeyError, reason:
        print("Error: %s" % reason)
        ret = ERR

    except Exception, reason:
        logging.error(reason)
        traceinfo = traceback.format_exc()
        traceback.print_exc()
        logging.debug(traceinfo)
        ret = ERR

    finally:
        # Close the OPS connection
        ops_conn.close()

    return ret

if __name__ == "__main__":
    main()
