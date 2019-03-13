import easygui
import os
import re

def regularMatch(path, regulars):
    # path = r'C:\Users\Ribbon\Desktop\全场景标准配置脚本V1.7.7'
    files = os.listdir(path)
    files = [os.path.join(path, file) for file in files]
    with open('自动生成文件文件夹/正则匹配结果.txt', 'a') as f:
        for file in files:
            f.write(file + '\n')
            with open(file, 'rb') as f1:
                infos = f1.read().decode('utf8', 'ignore')
                infos = infos.replace('\r', '')
                for regular in regulars:
                    gg = re.findall(regular, infos)
                    f.write(' '.join(gg) + '\n')
    easygui.msgbox('完成匹配... 匹配结果在 自动生成文件文件夹下 正则匹配结果.txt')

if __name__ == '__main__':
    regularMatch()
