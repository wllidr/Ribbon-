import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
import wmi

def ModifyWinNetConfig(ip, mark):
    print('正在修改IP')
    wmiService = wmi.WMI()

    colNicConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled = True)
    print(colNicConfigs)

    objNicConfig = colNicConfigs[0]
    arrIPAddresses = [ip]
    arrSubnetMasks = [mark]
    # arrDefaultGateways = [gateway]
    arrGatewayCostMetrics = [1]
    intReboot = 0

    # 设置IP掩码
    returnValue = objNicConfig.EnableStatic(IPAddress = arrIPAddresses, SubnetMask = arrSubnetMasks)

    # print(objNicConfig)
    if returnValue[0] == 0 or returnValue[0] == 1:
        print('更改成功')
        return True
    else:
        return False

    # 设置网关
    # returnValue = objNicConfig.SetGateways(DefaultIPGateway = arrDefaultGateways, GatewayCostMetric = arrGatewayCostMetrics)
    # if returnValue[0] == 0 or returnValue[0] == 1:
    #     pass
    # else:
    #     return False


def ftpServer(dirPath, account, password):
    # 实例化用户授权管理
    authorizer = DummyAuthorizer()
    authorizer.add_user(account, password, dirPath, perm='elradfmwMT')  # 添加用户 参数:username,password,允许的路径,权限
    authorizer.add_anonymous(os.getcwd())  # 这里是允许匿名用户,如果不允许删掉此行即可

    # 实例化FTPHandler
    handler = FTPHandler
    handler.authorizer = authorizer

    # 设定一个客户端链接时的标语
    handler.banner = "pyftpdlib based ftpd ready."

    # handler.masquerade_address = '151.25.42.11'#指定伪装ip地址
    # handler.passive_ports = range(60000, 65535)#指定允许的端口范围

    address = ('0.0.0.0', 21)  # FTP一般使用21,20端口
    server = ThreadedFTPServer(address, handler)  # FTP服务器实例

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # 开启服务器
    server.serve_forever()

if __name__ == '__main__':
    path = r'D:\shengkai\3.6\搭建FTP服务器\dist'
    ip = '192.168.0.1'
    mark = '255.255.255.0'
    ModifyWinNetConfig(ip, mark)
    ftpServer(path, 'root', '123456')
