from db.mysqlu import MysqlUse

def cheack_numbers():
    mysql = MysqlUse()
    datas = mysql.fetch(sql = 'select * from ippool')
    return len(datas)

def cheack_ip_datas():
    mysql = MysqlUse()
    datas = mysql.fetch(sql='select * from ippool')
    return datas