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

LOG_FILE_EXECUTE = 'ztp_delete.log'

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

def signal_handler(signum, frame):
    """Signal handler to ignore a signal"""
    pass

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
    stsIndex   = 0
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
        if rows2[0][index] == "Status":
            stsIndex = index

    # add grpNo and portIndex
    for item in rows2[1:]:
        if item[grpNoIndex] != '':
            if rows1['sysname'] == item[indexA]:
                d = dict(portIndex=item[portIndexA],grpNo=item[grpNoIndex],status=item[stsIndex],connIp='')
                portgroup_message.append(d)
            elif rows1['sysname'] == item[indexB]:
                d = dict(portIndex=item[portIndexB],grpNo=item[grpNoIndex],status=item[stsIndex],connIp='')
                portgroup_message.append(d)

    # add connection ip
    ifIndexA = 0
    ifIndexB = 0
    ifPortIndexA = 0
    ifPortIndexB = 0
    connIpA = 0
    connIpB = 0
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
    for i in range(len(portgroup_message)):
        for item in rows3[1:]:
            if item[ifIndexA] == rows1['sysname'] and item[ifPortIndexA] == portgroup_message[i]['portIndex']:
                portgroup_message[i]['connIp'] = item[connIpA]
                break
            elif item[ifIndexB] == rows1['sysname'] and item[ifPortIndexB] == portgroup_message[i]['portIndex']:
                portgroup_message[i]['connIp'] = item[connIpB]
                break
    logging.info("Port group message is %s" % portgroup_message)
    return portgroup_message

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

def _set_ztpEndFlag(ops_conn, endFlag):
    """Get the environment variable: ztpEndFlag"""
    logging.info("Set the environment variable: ztpEndFlag...")
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

def clear_port_identityTlv(ops_conn, intName):

    _ops = ops.ops()
    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + intName)
    _ops.cli.execute(handle,"undo identity enable")
    _ops.cli.execute(handle,"undo port identity")
    _ops.cli.execute(handle,"commit")
    _ops.cli.close(handle)

    return OK

def delete_logfile(ops_conn):

    _ops = ops.ops()
    handle,_ = _ops.cli.open()
    choice = {"Continue": "y", "continue": "y"}
    _ops.cli.execute(handle,"del /u " + LOG_FILE_EXECUTE,choice)
    _ops.cli.close(handle)

    return OK
    
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
    
def clear_portl3_conf(ops_conn,portMsg):

    _ops = ops.ops()

    handle, err_desp  = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"int " + portMsg['portIndex'])
    _ops.cli.execute(handle,"undo ip address")
    ret = _ops.cli.execute(handle,"portswitch")
    _ops.cli.execute(handle,"com")
    _ops.cli.close(handle)

    return OK
    
    
def clear_port_l3config(ops_conn, portMsg):
    # exit_ospf(ops_conn,portMsg['connIp'])
    clear_portl3_conf(ops_conn,portMsg)
    

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
    
def clear_ops_conf(ops_conn):
    _ops = ops.ops()
    handle,_ = _ops.cli.open()
    _ops.cli.execute(handle,"sys")
    _ops.cli.execute(handle,"ops")
    _ops.cli.execute(handle,"undo script-assistant python ztp_delete.py")
    _ops.cli.execute(handle,"comm")
    ret = _ops.cli.close(handle)



def main_proc(ops_conn):

    # create log file
    delete_logfile(ops_conn)
    log_init(LOG_FILE_EXECUTE, logging.INFO)

    #step 0: make sure the csv file is exist
    sysName = get_system_name(ops_conn)
    if sysName == None:
        logging.error("Get system name failed")
        return ERR
    #csvName = 'result_' + sysName + '.csv'
    csvName = sysName + '.csv'
    if not os.path.exists('/opt/vrpv8/home/' + csvName):
        logging.error("There is no file named %s, check AC please" % csvName)
        return ERR

    #step 1: set ztp end flag
    _set_ztpEndFlag(ops_conn, 1)

    #step 2: read csv file to get portgroup message
    rows1,rows2,rows3 = read_csv(csvName)
    portgroup_message = get_portgroup_message(rows1, rows2, rows3)

    #step 3: clear port identityTlv
    for i in range(len(portgroup_message)):
        clear_port_identityTlv(ops_conn, portgroup_message[i]['portIndex'])

    if "OUT_OF_BAND" in rows1['bandMgntMode'] and rows1['isReplace'] != "NO":
        logging.info("Current mode is out of band and replace,no need to clear port config")
    else:
        for i in range(len(portgroup_message)):
            if portgroup_message[i]['status'] == "fail":
                clear_port_l3config(ops_conn, portgroup_message[i])

    #step 4: delete csv file
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

    _ops.timer.countdown("e2", 1)
    
    _ops.correlate("e2")

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

    except IOError, reason:
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