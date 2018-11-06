from fabric.api import *
import pandas
import os
import hashlib
import time

# get('/opt/log/sys/sys-package1537157306.82.zip', r'D:\shengkai\3.6\fb')
# env.hosts=['root@12.255.4.249']
# env.password = 'Huawei23#$'
# # env.parallel = True

passwords = {}
infos = []
hosts = []

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

env.hosts = hosts
env.user = df.iloc[0, :]['账户'].strip()
env.passwords = passwords
env.warn_only = True

def fileConvert():
    # print(infos[hosts.index(env.host)]['upload'])
    if infos[hosts.index(env.host)]['upload']:
        for up in infos[hosts.index(env.host)]['upload']:
            for from_path, to_path in up.items():
                i = 0
                put(from_path, to_path)
                # while i < 3:
                #     md5FromPath = CalcMD5(from_path)
                #     print(md5FromPath, '------你------')
                #     print(from_path, to_path)
                #     put(from_path, to_path)
                #     time.sleep(10)
                #     md5ToPath = run('md5sum ' + to_path + '/' + os.path.basename(from_path))
                #     print(md5ToPath, '-------我-------')
                #     if md5FromPath in md5ToPath:
                #         print('相同, 上传结束')
                #         break
                #     i += 1

    if infos[hosts.index(env.host)]['download']:
        for down in infos[hosts.index(env.host)]['download']:
            for from_path, to_path in down.items():
                i = 0
                while i < 3:
                    md5FromPath = run('md5sum ' + from_path)
                    get(from_path, to_path)
                    md5ToPath = CalcMD5(to_path + '//' + os.path.basename(from_path))
                    if md5ToPath in md5FromPath:
                        print('相同, 结束')
                        break
                    i += 1

def runOther():
    if os.path.exists('script.txt'):
        with open('script.txt', 'r') as f:
            for line in f:
                if line.strip() == '':
                    pass
                else:
                    run(line)

def CalcMD5(filepath):
    '''MD5加密，用于校验保证完整性'''
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash

def go():
    execute(fileConvert)
    execute(runOther)

