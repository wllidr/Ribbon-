from db.mysqlu import MysqlUse

def login(user, passwd):
    msql = MysqlUse()
    sql = "select * from user where name = '%s' and passwd = '%s'" %(user, passwd)
    data = msql.fetch(sql)
    if len(data) > 0:
        return 'OK'
    else:
        return '账号密码错误请重新确认'