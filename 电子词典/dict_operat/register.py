from db.mysqlu import MysqlUse
def register(user, passwd):
    msql = MysqlUse()
    sql = "select * from user where name = '%s' and passwd = '%s'" % (user, passwd)
    data = msql.fetch(sql)
    if not data:
        sql = "insert into user (name, passwd) VALUES ('%s', '%s')" % (user, passwd)
        msql.excute(sql)
        return '添加账户成功'
    else:
        return '该账户早已经存在'
