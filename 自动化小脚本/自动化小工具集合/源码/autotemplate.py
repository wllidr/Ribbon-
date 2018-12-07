'''
    自动化模板生成脚本工具
'''
import easygui
import pandas as pd
import os
import re

def config(filePath):
    '''
        :param filePath: 配置excel的路径
        :return: 配置参数
    '''
    sheet_config = '配置参数'
    configVariables = pd.read_excel(filePath, sheet_name = sheet_config).T
    index = configVariables.ix[0, :].tolist()
    index = [s.lower() for s in index]
    configVariables = configVariables.ix[:, :].T
    return index, configVariables

def templete(filePath, templeteRow):
    '''
        :param filePath: 配置excel的路径
        :return: 模板参数
    '''
    sheet_templete = '配置模板'
    templeteVariabeles1 = pd.read_excel(filePath, sheet_name=sheet_templete, header=None)
    row = ord(templeteRow) - 65
    templeteVariabeles1 = templeteVariabeles1.ix[:, row]

    return templeteVariabeles1

def saveConfig(templete, templeteVariables, configVariables, savePath):
    '''
        :param templete:  模板
        :param templeteVariables:  模板的所有所需变量
        :param configVariables: 配置参数
        :param savePath: 保存配置路径
        :return: 将配置进行保存
    '''
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    # print(configVariables.shape[0])
    for i in range(configVariables.shape[0]):
        filePath = savePath + '\\' + str(configVariables.iloc[i, :].iloc[0]) + '.txt'
        f = open(filePath, 'w')
        for j in range(templete.shape[0]):
            line = templete.iloc[j]
            groups = re.findall('<.*?>', line)
            # print(groups)
            if groups:
                try:
                    for g in groups:
                        line = re.sub(g, str(configVariables.iloc[i, :][g.lower()]), line)
                    f.write(line + '\n')
                except Exception:
                    f.write(line + '\n')
            else:
                f.write(line + '\n')
        # f.close()

def begin_template(filePath, templeteRow, savePath):
    print('开始生成脚本配置..............')
    if filePath == '':
        filePath = '工具表格模板.xls'
    if templeteRow == '':
        templeteRow = 'A'
    if savePath == '':
        savePath = 'Scripts'
    templeteRow = templeteRow.upper()

    templeteVariables, configVariables = config(filePath)
    templete1 = templete(filePath, templeteRow)
    templete1 = templete1.dropna(axis=0, how='all')
    templete1.index = [x for x in range(templete1.shape[0])]
    try:
        saveConfig(templete1, templeteVariables, configVariables, savePath)
    except:
        pass
    print('生成脚本配置完成..............')
    easygui.msgbox('自动模板配置生成完成.....', title='提示框')
