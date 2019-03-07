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
import time
import easygui

if not os.path.exists('自动生成文件文件夹'):
    os.makedirs('自动生成文件文件夹')

if not os.path.exists('自动生成文件文件夹/上传下载日志'):
    os.makedirs('自动生成文件文件夹/上传下载日志')
passwords = {}
infos = []
hosts = []
t = time.strftime('%Y%m%d_%H%M', time.localtime())

'''
    日志信息参数
'''
logger = logging.getLogger(t + 'Fabric')
formatter = logging.Formatter('%(message)s')
fileHandler = logging.FileHandler('自动生成文件文件夹/上传下载日志/' + t + 'FabricLog.txt')
fileHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

'''
    初始值
'''
env.hosts = ''
env.user = ''
env.passwords = ''
env.warn_only = ''

'''
    文件传输
'''
def fileConvert(retry = 3):
    # print(infos[hosts.index(env.host)]['upload'])
    if infos[hosts.index(env.host)]['upload']:
        for up in infos[hosts.index(env.host)]['upload']:
            for from_path, to_path in up.items():
                i = 0
                # put(from_path, to_path)
                while i < retry:
                    md5FromPath = CalcMD5(from_path)
                    put(from_path, to_path)
                    md5ToPath = run('md5sum ' + to_path + '/' + os.path.basename(from_path))
                    if md5FromPath in md5ToPath:
                        logger.info(env.host + ' :' + from_path + ' 上传到 ' + to_path + ' 成功')
                        break
                    i += 1
                    if i == retry:
                        logger.info(env.host + ' :' + from_path + ' 上传到 ' + to_path + ' 失败')

    if infos[hosts.index(env.host)]['download']:
        for down in infos[hosts.index(env.host)]['download']:
            for from_path, to_path in down.items():
                i = 0
                while i < retry:
                    md5FromPath = run('md5sum ' + from_path)
                    get(from_path, to_path)
                    md5ToPath = CalcMD5(to_path + '//' + os.path.basename(from_path))
                    if md5ToPath in md5FromPath:
                        logger.info(env.host + ' :' + from_path + ' 下载到 ' + to_path + ' 成功')
                        break
                    i += 1
                    if i == retry :
                        logger.info(env.host + ' :' + md5FromPath + ' 下载到 ' + to_path + ' 失败')
                        time.sleep(1)
                        if os.path.exists(to_path):
                            os.remove(to_path)

'''
    跑脚本，可以进行升级，查询等等操作，再script.txt上写好指令
'''
def runOther():
    if os.path.exists('fabscript.txt'):
        logger.info('\n\n------' + env.host + '的脚本所有指令结果如下-------')
        with open('fabscript.txt', 'r') as f:
            for line in f:
                if line.strip() == '':
                    pass
                else:
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
    执行流程
'''
@runs_once
def go():
    execute(fileConvert)
    execute(runOther)

def begin_fabfile(file):
    '''
        excel文件信息读取
    '''
    try:
        df = pandas.read_excel(file, sheet_name='服务器文件上传下载')
    except:
        df = pandas.read_excel(file, sheet_name='Sheet1')
    df = df.fillna(method='ffill', axis=0)
    # print(df.iloc[0, :])
    for i in range(df.shape[0]):
        info = df.iloc[i, :]
        # print(info)
        passwords[
            str(info['账户']).strip() + '@' + str(info['设备IP']).strip() + ':' + str(int(info['端口号'])).strip()] = str(
            info['密码']).strip()

        if str(info['设备IP']).strip() not in hosts:
            temp1 = {'ip': str(info['设备IP']).strip(), 'download': [], 'upload': []}
            hosts.append(str(info['设备IP']).strip())
            if str(info['方式（upload | download | none）']).strip() == 'upload':
                temp1['upload'].append({str(info['源路径']).strip(): str(info['目标路径']).strip()})
            elif str(info['方式（upload | download | none）']).strip() == 'download':
                temp1['download'].append({str(info['源路径']).strip(): str(info['目标路径']).strip()})
            else:
                pass
            infos.append(temp1)
        else:
            if str(info['方式（upload | download | none）']).strip() == 'upload':
                infos[hosts.index(str(info['设备IP']))]['upload'].append(
                    {str(info['源路径']).strip(): str(info['目标路径']).strip()})
            elif str(info['方式（upload | download | none）']).strip() == 'download':
                infos[hosts.index(str(info['设备IP']))]['download'].append(
                    {str(info['源路径']).strip(): str(info['目标路径']).strip()})
            else:
                pass
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
    execute(go)

if __name__ == '__main__':
    print('开始文件传输跟刷脚本.........')
    begin_fabfile()
    print('文件传输跟刷脚本结束.........')
    easygui.msgbox('文件传输跟刷脚本结束')

logger.removeHandler(fileHandler)
