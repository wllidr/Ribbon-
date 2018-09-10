REMOTE_PATH_MD5 = ''

def read_csv():
    """This function resolves the CSV file and returns system information, L2 link information, L3 link information"""
    rows1 = []
    rows2 = []
    rows3 = []
    device = {}
    table1 = True
    table2 = False
    table3 = False
    for line in open('Agile-Controller-DCN.csv'):
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

def get_basiccfg_name(rows1):
    basicCfgName = 'basic_spine.cfg'
    Role = rows1["device role"].lower()
    if Role == 'leaf':
        print 'stack', rows1['stack']
        if rows1["stack"] != '':
            basicCfgName = 'basic_leaf_stack.cfg'
        else:
            basicCfgName = 'basic_leaf_single_mlag.cfg'
    return basicCfgName

def main_proc():
    rows1, rows2, rows3 = read_csv()
    rows1 = change_lower(rows1)
    # print 'rows1'
    # print rows1
    # print 'rows2'
    # print rows2
    # print 'rows3'
    # print rows3
    xftp_user = rows1['xftp server user']
    xftp_password = rows1['xftp server passwd']
    xftp_ip = rows1['xftp server ip']
    xftp_port = rows1['xftp server port']
    print xftp_user, xftp_password, xftp_ip, xftp_port
    FILE_SERVER = 'sftp://' + xftp_user + ':' + xftp_password + '@' + xftp_ip + ':' + xftp_port
    print 'FILE_SERVER', FILE_SERVER
    REMOTE_PATH_CONFIG = get_basiccfg_name(rows1)
    print 'REMOTE_PATH_CONFIG', REMOTE_PATH_CONFIG


def main(usb_path = ''):
    """The main function of user script. It is called by ZTP frame, so do not remove or change this function.

    Args:
    Raises:
    Returns: user script processing result
    """
    host = "localhost"
    if usb_path and len(usb_path):
        logging.info('ztp_script usb_path: %s', usb_path)
        global FILE_SERVER
        FILE_SERVER = 'file:///' + usb_path
    ret = main_proc()


if __name__ == "__main__":
    main()