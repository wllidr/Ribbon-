'''
    Date : 2018-11-06
    Author : Ribbon Huang
    Description:
        Fabric写的用于自动上传下载文件，以及刷脚本指令如更新查询等
'''
from fabric.api import *
import pandas
import os
import hashlib
import logging
import re

passwords = {}
infos = []
hosts = []

'''
    日志信息参数
'''
logger = logging.getLogger('Fabric')
formatter = logging.Formatter('%(message)s')
fileHandler = logging.FileHandler('FabricLog.txt')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


'''
    excel文件信息读取
'''
file = r'文件传输.xls'
df = pandas.read_excel(file)
df = df.fillna(method='ffill', axis=0)
for i in range(df.shape[0]):
    info = df.iloc[i, :]
    # print(info)
    passwords[str(info['账户']).strip() + '@' + str(info['设备IP']).strip() + ':' + str(int(info['端口号'])).strip()] = str(info['密码']).strip()

    if str(info['设备IP']).strip() not in hosts:
        temp1 = { 'ip': str(info['设备IP']).strip(), 'download':  [], 'upload' :[]}
        hosts.append(str(info['设备IP']).strip())
        if str(info['方式（upload | download）']).strip() == 'upload':
            temp1['upload'].append({str(info['源路径']).strip(): str(info['目标路径']).strip()})
        else:
            temp1['download'].append({str(info['源路径']).strip() : str(info['目标路径']).strip()})
        infos.append(temp1)
    else:
        if str(info['方式（upload | download）']).strip() == 'upload':
            infos[hosts.index(str(info['设备IP']))]['upload'].append({str(info['源路径']).strip(): str(info['目标路径']).strip()})
        else:
            infos[hosts.index(str(info['设备IP']))]['download'].append({str(info['源路径']).strip() : str(info['目标路径']).strip()})
# print(infos)
# print(passwords)
# print(hosts)

'''
    初始值
'''
env.hosts = hosts
env.user = df.iloc[0, :]['账户'].strip()
env.passwords = passwords
env.warn_only = True

'''
    文件传输
'''
def fileConvert():
    # print(infos[hosts.index(env.host)]['upload'])
    global logger
    if infos[hosts.index(env.host)]['upload']:
        for up in infos[hosts.index(env.host)]['upload']:
            for from_path, to_path in up.items():
                i = 0
                # put(from_path, to_path)
                while i < 3:
                    md5FromPath = CalcMD5(from_path)
                    put(from_path, to_path)
                    md5ToPath = run('md5sum ' + to_path + '/' + os.path.basename(from_path))
                    if md5FromPath in md5ToPath:
                        logger.info(from_path + ' 上传到 ' + to_path + ' 成功')
                        break
                    i += 1
                    if i == 3:
                        logger.info(from_path + ' 上传到 ' + to_path + ' 失败')

    if infos[hosts.index(env.host)]['download']:
        for down in infos[hosts.index(env.host)]['download']:
            for from_path, to_path in down.items():
                i = 0
                while i < 3:
                    md5FromPath = run('md5sum ' + from_path)
                    get(from_path, to_path)
                    md5ToPath = CalcMD5(to_path + '//' + os.path.basename(from_path))
                    if md5ToPath in md5FromPath:
                        logger.info(from_path + ' 下载到 ' + to_path + ' 成功')
                        break
                    i += 1
                    if i == 3 :
                        logger.info(md5FromPath + ' 下载到 ' + to_path + ' 失败')

'''
    跑脚本，可以进行升级，查询等等操作，再script.txt上写好指令
'''
def runOther():
    global logger
    if os.path.exists('script.txt'):
        with open('script.txt', 'r') as f:
            for line in f:
                if line.strip() == '':
                    pass
                else:
                    logger.info('-------------')
                    logger.info(line)
                    info = run(line)
                    logger.info(re.sub('\r\n', '\n', info))
    else:
        pass

def CalcMD5(filepath):
    '''MD5加密，用于校验保证完整性'''
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash

'''
    用于执行流程 ： 黑框执行  fab go
'''
def go():
    global logger
    execute(fileConvert)
    execute(runOther)
    logger.removeHandler(fileHandler)