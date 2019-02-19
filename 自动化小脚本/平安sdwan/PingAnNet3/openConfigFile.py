import os
import zipfile

def OpenConfigFile():
    path = [file for file in os.listdir('.') if '全场景标准配置脚本' in file][0]
    zf = zipfile.ZipFile(path)
    return zf

    # with zf.open(fileName, mode='r', pwd='Pingan123'.encode('utf-8')) as f:
    #     for line in f:
    #         try:
    #             print(line.decode('utf8'))
    #         except:
    #             print(line.decode('gbk', 'ignore'))

if __name__ == '__main__':
    OpenConfigFile('Access-SW-3700EI-╡Ñ╗·.txt')