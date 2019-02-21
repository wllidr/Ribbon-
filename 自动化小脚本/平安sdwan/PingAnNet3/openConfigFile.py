import os
import zipfile

def OpenConfigFile():
    path = [file for file in os.listdir('.') if '全场景标准配置脚本' in file][0]
    zf = zipfile.ZipFile(path)
    return zf

if __name__ == '__main__':
    OpenConfigFile('Access-SW-3700EI-╡Ñ╗·.txt')