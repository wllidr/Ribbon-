'''
    自动化模板生成脚本工具
'''
import pandas as pd
import os
import re

def config(filePath):
    '''
        :param filePath: 配置excel的路径
        :return: 配置参数
    '''
    sheet_config = '配置参数'
    df2 = pd.read_excel(filePath, sheet_name = sheet_config)
    df2.columns = [column.strip() for column in df2.columns]
    return df2

def templete(filePath, templeteRow):
    '''
        :param filePath: 配置excel的路径
        :return: 模板参数
    '''
    sheet_templete = '配置模板'
    df1 = pd.read_excel(filePath, sheet_name=sheet_templete, header=None)
    row = ord(templeteRow) - 65
    df1 = df1.ix[:, row]
    return df1.tolist()

def saveConfig(df1, df2, savePath):
    '''
        :param templete:  模板
        :param templeteVariables:  模板的所有所需变量
        :param configVariables: 配置参数
        :param savePath: 保存配置路径
        :return: 将配置进行保存
    '''
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    # print(df2)
    for i in range(df2.shape[0]):
        # print(df2.iloc[i , 0])
        # print(df2.loc[i, '<SYSNAME>'])
        if os.path.exists(savePath + '/' + df2.iloc[i, 0]+'.txt'):
            os.remove(savePath + '/' + df2.iloc[i, 0]+'.txt')
        with open(savePath + '/' + df2.iloc[i, 0]+'.txt', 'w') as f:
            for line in df1:
                allReplace = re.findall('<[\s\S]*?>', line)
                if allReplace:
                    for replace in allReplace:
                        # print(replace)
                        # print(df2.loc[i, replace])
                        line = re.sub(replace, str(df2.loc[i, replace]), line)
                f.write(line + '\n')

def begin_template(filePath, templeteRow, savePath):
    print('使用自动生成配置模板........')
    # print('开始生成脚本配置..............')
    if filePath == '':
        filePath = '工具表格模板.xls'
    if templeteRow == '':
        templeteRow = 'A'
    if savePath == '':
        savePath = 'Scripts'
    templeteRow = templeteRow.upper()
    df1 = templete(filePath, templeteRow)
    df2 = config(filePath)
    saveConfig(df1, df2, savePath)
    print('配置生成成功........')
    # print(df1)

if __name__ == '__main__':
    begin_template(r'C:\Users\Ribbon\Desktop\工作\润迅\自动化小工具集合\1.xlsx', '', '')
